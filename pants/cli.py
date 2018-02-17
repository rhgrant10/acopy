# -*- coding: utf-8 -*-

"""Console script for pants."""
import re
import json
import time
import math
import string
import random
import logging
import collections
import datetime

import click
import statsd
import numpy as np
import networkx
from matplotlib import pyplot as plt

import pants


now = datetime.datetime.now()
log_filename = f'genetic_{now.isoformat()}.log'


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


TEST_COORDS_33 = [
    (34.021150, -84.267249), (34.021342, -84.363437), (34.022585, -84.362150),
    (34.022718, -84.361903), (34.023101, -84.362980), (34.024302, -84.163820),
    (34.044915, -84.255772), (34.045483, -84.221723), (34.046006, -84.225258),
    (34.048194, -84.262126), (34.048312, -84.208885), (34.048679, -84.224917),
    (34.049510, -84.226327), (34.051529, -84.218865), (34.055487, -84.217882),
    (34.056326, -84.200580), (34.059412, -84.216757), (34.060164, -84.242514),
    (34.060461, -84.237402), (34.061281, -84.334798), (34.063814, -84.225499),
    (34.061468, -84.334830), (34.061518, -84.243566), (34.062461, -84.240155),
    (34.064489, -84.225060), (34.066471, -84.217717), (34.068455, -84.283782),
    (34.068647, -84.283569), (34.071628, -84.265784), (34.105840, -84.216670),
    (34.109645, -84.177031), (34.116852, -84.163971), (34.118162, -84.163304),
]


class PrintoutPlugin(pants.solver.SolverPlugin):
    def initialize(self, solver):
        super().initialize(solver)
        self.log = get_logger()
        self.iteration = 0
        self.best_count = 0
        self.width = None

    def on_start(self, state):
        self.width = math.ceil(math.log10(state.limit)) + 2

    def on_iteration(self, state):
        report = f'{self.iteration: {self.width}d}'
        self.iteration += 1
        if state.is_new_record:
            self.best_count += 1
            end = '\n'
            report += (f' {self.best_count: {self.width}d} \t{state.best}')
            if hasattr(state.ants[0], 'dna'):
                report += f' {state.ants[0].dna}'
        else:
            end = '\r'
        self.log.info(report, end=end)

    def on_finish(self, state):
        self.log.info('Done' + ' ' * self.width)


def dist(a, b):
    (x1, y1), (x2, y2) = a, b
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def get_test_world_33():
    graph = collections.defaultdict(dict)
    for i, start in enumerate(TEST_COORDS_33):
        a = string.printable[i]
        for j, end in enumerate(TEST_COORDS_33[i + 1:], i + 1):
            b = string.printable[j]
            graph[a][b] = {'weight': dist(start, end)}
    return networkx.Graph(graph)


def graph_as_dict(graph):
    data = collections.defaultdict(dict)
    for u, v in graph.edges:
        data[u][v] = graph.edges[u, v]
    return dict(data)


def generate_random_graph(size=10, min_weight=1, max_weight=50):
    graph = networkx.complete_graph(string.printable[:size])
    for e in graph.edges:
        w = random.randint(min_weight, max_weight)
        graph.edges[e]['weight'] = w
    return graph


def read_graph_from_file(filepath):
    with open(filepath) as f:
        data = json.load(f)
    graph = networkx.Graph(data)
    return graph


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
        colony = pants.Colony(alpha=self.genes['alpha'],
                              beta=self.genes['beta'], seed=choice_seed)
        # create the solver
        solver = pants.Solver(rho=self.genes['rho'], q=self.genes['q'],
                              top=int(self.genes['top']))
        solver.add_plugin(pants.plugins.TimeLimitPlugin(limit))

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


class BadPerformance(pants.Solution):
    def __init__(self):
        super().__init__(graph=None, start=None)
        self.weight = math.inf


class Parser:
    def __init__(self, filepath, pause=None):
        self.filepath = filepath
        self.line = None
        self.generation = 0
        self.settings = {}
        if pause is None:
            def pause():
                time.sleep(1)
        self.pause = pause
        self.fp = open(self.filepath)

    def __iter__(self):
        self.parse_setting()
        return self

    def __next__(self):
        print(f"Parsing generation #{self.generation}")
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


class Simulator:
    def __init__(self, graph, population=1000, limit=15, seed=None,
                 choice_seed=None):
        self.log = get_logger()
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
            self.log.info(f'[gen:{self.gen}][species:{species}][composition] '
                          f'{percentage:>3.1f}%')

        # test and print the performance of each creature
        performances = []
        for i, creature in enumerate(self.creatures, 1):
            try:
                optimizer = creature.optimize(self.graph, limit=self.limit)
                for performance in optimizer:
                    print(f'[gen:{self.gen}][solver:{i}]'
                          f'[species:{creature.species}][trial] '
                          f'{performance.weight}', end='\r', flush=True)
            except Exception:
                self.log.exception(f'[gen:{self.gen}][test:{i}][ERROR]')
                performance = BadPerformance()
            finally:
                performances.append(performance)
                self.log.info(f'[gen:{self.gen}][solver:{i}]'
                              f'[species:{creature.species}][trial] '
                              f'{performance.weight}')

        # print performance statistics
        performances, creatures = self.sort(performances, self.creatures)
        weights = [p.weight for p in performances]
        b, m, w = self.get_bmw(creatures, weights)
        bc, mc, wc = creatures[b], creatures[m], creatures[w]
        bw, mw, ww = weights[b], weights[m], weights[w]
        self.log.info(f'[gen:{self.gen}][stat:best][species:{bc.species}] {bw}')
        self.log.info(f'[gen:{self.gen}][stat:median][species:{mc.species}] {mw}')
        self.log.info(f'[gen:{self.gen}][stat:worst][species:{wc.species}] {ww}')

        # breed a new generation
        self.creatures = list(self.procreate(self.filter(creatures)))
        self.gen += 1

    def run_forever(self):
        try:
            while True:
                self.run_generation()
        except KeyboardInterrupt as e:
            self.log.info('Stopped')

    def get_bmw(self, creatures, weights):
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


@click.group()
@click.option('--global-seed', type=int, default=None)
def main(global_seed):
    global_seed = global_seed or hash(time.time())
    get_logger().info(f"[setting:global-seed] {global_seed}")
    random.seed(global_seed)


@main.command('statsd')
@click.option('--logfile', type=click.Path(dir_okay=False, readable=True))
def statsd_output(logfile):
    parser = Parser(logfile)
    statsd_client = statsd.StatsClient(prefix=f"pants.genetic.{int(time.time())}")
    for generation in parser:
        gen = f'generation.{generation["index"]}'
        with statsd_client.pipeline() as pipe:
            for species, percentage in generation['composition'].items():
                pipe.gauge(f'{gen}.composition.{species}',
                           percentage)

            for i, trial in enumerate(generation['trials']):
                pipe.gauge(f'trial.{i}.score', trial['score'])
                pipe.set(f'{gen}.trial.species', trial['species'])
                pipe.set(f'species', trial['species'])


@main.command('plot')
@click.option('--logfile', type=click.Path(dir_okay=False, readable=True))
def matplotlib_output(logfile):
    parser = Parser(logfile, lambda: plt.pause(0.1))
    data = []
    plt.ion()
    for generation in parser:
        scores = [t['score'] for t in generation['trials']]
        data.append(list(sorted(scores)))
        plt.gca().clear()
        plt.plot(data)


@main.command()
@click.option('--stats/--no-stats', default=False)
@click.option('--reset', type=int, default=False)
@click.option('--threshold', type=float, default=None)
@click.option('--flip', type=int, default=False)
@click.option('--evo/--no-evo', default=False)
@click.option('--elite', default=0.0)
@click.option('--darwin', default=0.0)
@click.option('--plot/--no-plot', default=False)
@click.option('--file', type=click.Path(dir_okay=False, readable=True))
@click.option('--size', type=int, default=60)
@click.option('--limit', default=2000)
@click.option('--q', default=1.0)
@click.option('--rho', default=0.03)
@click.option('--beta', default=3.0)
@click.option('--alpha', default=1.0)
def demo(alpha, beta, rho, q, limit, size, file, plot, darwin, elite, evo,
         flip, threshold, reset, stats):
    args = '\n'.join([
        'alpha={alpha} beta={beta} rho={rho}',
        'limit={limit} gen-size={size} elite={elite}',
        'reset={reset} evo={evo} darwin(f)={darwin} '
        'flip(f)={flip} plot={plot}',
    ])
    get_logger().info(args.format(**locals()))

    graph = read_graph_from_file(file) if file else get_test_world_33()

    colony = pants.Colony(alpha=alpha, beta=beta)
    solver = pants.Solver(rho=rho, q=q)
    solver.add_plugin(PrintoutPlugin())
    solver.add_plugin(pants.plugins.TimerPlugin())

    if plot:
        solver.add_plugin(pants.plugins.StatRecorder())
    if darwin:
        solver.add_plugin(pants.plugins.DarwinPlugin(sigma=darwin))
    if elite:
        solver.add_plugin(pants.plugins.EliteTracer(factor=elite))
    if reset:
        solver.add_plugin(pants.plugins.PeriodicReset(period=reset))
    if evo:
        solver.add_plugin(pants.plugins.SelfishGenePlugin())
    if flip:
        solver.add_plugin(pants.plugins.PheromoneFlip(period=flip))
    if stats:
        solver.add_plugin(pants.plugins.StatsdPlugin())
    if threshold:
        solver.add_plugin(pants.plugins.ThresholdPlugin(threshold))

    solver.solve(graph, colony, gen_size=size, limit=limit)


@main.command()
@click.option('--choice-seed', type=int, default=None)
@click.option('--evo-seed', type=int, default=None)
@click.option('--file', type=click.Path(dir_okay=False, readable=True))
@click.option('--limit', default=10)
@click.option('--population', default=1000)
def genetic(population, limit, file, evo_seed, choice_seed):
    seeds = random.randint(0, 2 ** 32 - 1), random.randint(0, 2 ** 32 - 1)
    if not choice_seed:
        choice_seed = seeds[0]

    if not evo_seed:
        evo_seed = seeds[1]

    log = get_logger()
    log.info(f"[setting:evo-seed] {evo_seed}")
    log.info(f"[setting:choice-seed] {choice_seed}")

    graph = read_graph_from_file(file) if file else get_test_world_33()
    simulator = Simulator(graph=graph, population=population, limit=limit,
                          seed=evo_seed, choice_seed=choice_seed)
    simulator.run_forever()


@main.command()
@click.option('--max-weight', default=50.0)
@click.option('--min-weight', default=1.0)
@click.option('--size', default=10)
@click.option('--file', type=click.Path(dir_okay=False, writable=True))
def create(file, size, min_weight, max_weight):
    graph = generate_random_graph(size=size, min_weight=min_weight,
                                  max_weight=max_weight)
    data = graph_as_dict(graph)
    if file:
        with open(file, 'w') as f:
            json.dump(data, f)
    else:
        get_logger().info(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
