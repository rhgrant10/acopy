# -*- coding: utf-8 -*-
import collections
import logging
import math
import re

import numpy as np

from . import ant
from . import solvers
from . import plugins
from . import utils


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Creature:
    mutation_rate = 0.25
    fgenes = {
        'alpha': lambda v: int(v * 10),
        'beta': lambda v: int(v * 10),
        'rho': lambda v: int(v * 10),
        'q': lambda v: int(v * 10),
        'top': int,
        'gen_size': int,
    }

    def __init__(self, genes, seed=None):
        self.genes = genes
        self.seed = seed
        self.rng = np.random.RandomState(seed=seed)

    @classmethod
    def from_random(cls, seed=None, **kwargs):
        rng = np.random.RandomState(seed=seed)
        gen_size = rng.randint(1, 100)
        kwargs['genes'] = {
            'alpha': 10 * rng.rand(),
            'beta': 10 * rng.rand(),
            'rho': rng.rand(),
            'q': 10 * rng.rand(),
            'gen_size': gen_size,
            'top': rng.randint(0, gen_size),
        }
        return cls(seed=seed, **kwargs)

    @property
    def species(self):
        names = []
        for attr, value in sorted(self.genes.items()):
            gene = self.fgenes[attr](value)
            names.append(f'{attr[0]}{gene}')
        return ''.join(names)

    def optimize(self, graph, limit=15, choice_seed=None):
        # create the colony
        colony = ant.Colony(alpha=self.genes['alpha'], beta=self.genes['beta'],
                            seed=choice_seed)
        # create the solver
        solver = solvers.Solver(rho=self.genes['rho'], q=self.genes['q'],
                                top=int(self.genes['top']))
        solver.add_plugin(plugins.TimeLimitPlugin(limit))

        # optimize the fuck outta that graph
        return solver.optimize(graph.copy(), colony, limit=None,
                               gen_size=int(self.genes['gen_size']))

    def make_child(self, mutation_rate=0.05):
        copy = {}
        for attr, value in self.genes.items():
            if self.rng.rand() < self.mutation_rate:
                value = self.rng.normal(value, .5)
            copy[attr] = value
        return self.__class__(genes=copy, seed=self.seed)


class BadPerformance(solvers.Solution):
    def __init__(self):
        super().__init__(graph=None, start=None)
        self.weight = math.inf


class Simulator:
    def __init__(self, graph, population=1000, limit=15, seed=None):
        self.rng = np.random.RandomState(seed=seed)
        self.graph = graph
        self.limit = limit
        self.population = population
        self.gen = 0
        m = 2 ** 32 - 1
        seeds = [self.rng.randint(0, m) for __ in range(population)]
        self.creatures = [Creature.from_random(seed) for seed in seeds]

    def run_generation(self):
        # print generation composition
        for species, percentage in self.get_population_composition():
            logger.info(f'[gen:{self.gen}][species:{species}][composition] '
                        f'{percentage:>3.1f}%')

        # test and print the performance of each creature
        performances = []
        for i, creature in enumerate(self.creatures, 1):
            try:
                optimizer = creature.optimize(self.graph, limit=self.limit)
                trials = list(optimizer)
                performance = trials[-1]
            except Exception:
                logger.exception(f'[gen:{self.gen}][test:{i}][ERROR]')
                performance = BadPerformance()
            finally:
                performances.append(performance)
                logger.info(f'[gen:{self.gen}][solver:{i}]'
                            f'[species:{creature.species}][trial] '
                            f'{performance.weight}')

        # print performance statistics
        performances, creatures = self.sort(performances, self.creatures)
        weights = [p.weight for p in performances]
        b, m, w = self.get_bmw(creatures, weights)
        bc, mc, wc = creatures[b], creatures[m], creatures[w]
        bw, mw, ww = weights[b], weights[m], weights[w]
        logger.info(f'[gen:{self.gen}][stat:best][species:{bc.species}] {bw}')
        logger.info(f'[gen:{self.gen}][stat:median][species:{mc.species}] {mw}')
        logger.info(f'[gen:{self.gen}][stat:worst][species:{wc.species}] {ww}')

        # breed a new generation
        self.creatures = list(self.procreate(self.filter(creatures)))
        self.gen += 1

    def run_forever(self):
        try:
            while True:
                self.run_generation()
        except KeyboardInterrupt as e:
            logger.info('Stopped')

    def get_bmw(self, creatures, weights):
        # get best, median, worst
        return 0, len(creatures) // 2, -1

    def get_population_composition(self):
        histogram = collections.Counter([c.species for c in self.creatures])
        n = len(self.creatures)
        yield from [(s, 100 * v / n) for s, v in histogram.most_common()]

    def sort(self, performances, creatures):
        data = list(zip(performances, range(len(performances)), creatures))
        data.sort()
        performances, __, creatures = zip(*data)
        return performances, list(creatures)

    def filter(self, creatures):
        n = len(creatures)
        h = n // 2
        back_half = creatures[h:]
        self.rng.shuffle(back_half)
        creatures[h:] = back_half
        for i in range(h):
            if self.rng.rand() < i / n:
                j = n - i
                creatures[i], creatures[j] = creatures[j], creatures[i]
        return creatures[:h]

    def procreate(self, creatures, count=2):
        for creature in creatures:
            yield creature
            for __ in range(count - 1):
                yield creature.make_child()


class Parser:
    def __init__(self, filepath, pause=None):
        self.filepath = filepath
        self.line = None
        self.generation = 0
        self.settings = {}
        self.pause = pause or utils.noop
        self.fp = open(self.filepath)

    def __iter__(self):
        self.parse_setting()
        return self

    def __next__(self):
        logger.info(f"Parsing generation #{self.generation}")
        generation = self.parse_generation()
        self.generation += 1
        return generation

    def wait_for_next_line(self):
        line = self.fp.readline()
        while not line:
            self.pause()
            line = self.fp.readline()
        self.line = line

    def parse_generation(self):
        self.wait_for_next_line()
        composition = self.parse_composition()
        trials = self.parse_trials()
        self.parse_stats()
        return {
            'composition': composition,
            'trials': trials,
            'index': self.generation,
        }

    def parse_setting(self):
        self.wait_for_next_line()
        setting_re = re.compile(r'\[setting:(?P<name>.+)\] (?P<value>.*)')
        while 'setting' in self.line:
            name, value = setting_re.search(self.line).groups()
            self.settings[name] = value
            self.wait_for_next_line()

    def parse_composition(self):
        composition = {}
        comp_re = re.compile(r'\[gen:(?P<generation>.+)\]'
                             r'\[species:(?P<species>.+)\]'
                             r'\[composition\] (?P<composition>.*)')
        while 'composition' in self.line:
            data = comp_re.search(self.line).groupdict()
            composition[data['species']] = float(data['composition'].strip("%"))
            self.wait_for_next_line()
        return composition

    def parse_trials(self):
        trials = []
        trial_re = re.compile(r'\[gen:(?P<generation>.+)\]'
                              r'\[solver:(?P<solver>.+)\]'
                              r'\[species:(?P<species>.+)\]'
                              r'\[trial\] (?P<trial>.*)')
        while 'trial' in self.line:
            data = trial_re.search(self.line).groupdict()
            trials.append({"species": data['species'],
                           "score": float(data['trial'])})
            self.wait_for_next_line()
        return trials

    def parse_stats(self):
        while 'stat' in self.line:
            self.wait_for_next_line()
        return None
