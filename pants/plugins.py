import time
import random
import collections
import functools

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import statsd
except ImportError:
    pass

from .solver import SolverPlugin
from .ant import Ant


class GeneticAnt(Ant):
    def __init__(self, *args, **kwargs):
        self.dna = kwargs.pop("dna", self.get_random_dna())
        self.mutation_rate = kwargs.pop("mutation_rate", 0.1)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_ant(cls, ant, **kwargs):
        return cls(ant.alpha, ant.beta, **kwargs)

    def get_random_dna(self):
        return (f"{random.choice('Aa')}"
                f"{random.choice('Aa')}"
                f"{random.choice('Bb')}"
                f"{random.choice('Bb')}")

    def get_gamete_dna(self):
        a = random.choice(self.dna[:2])
        b = random.choice(self.dna[2:])
        return self.mutate(a), self.mutate(b)

    def mutate(self, allele):
        if random.random() < self.mutation_rate:
            if allele.islower():
                return allele.upper()

            return allele.lower()

        return allele


class EliteTracer(SolverPlugin):
    def __init__(self, factor=1):
        self.factor = factor

    def on_iteration(self, state):
        state.best.trace(self.solver.q * self.factor)


class PeriodicActionPlugin(SolverPlugin):
    def __init__(self, period=50):
        self.period = period
        self.index = None

    def initialize(self, solver):
        super().initialize(solver)
        self.index = 0

    def on_iteration(self, state):
        self.index = (self.index + 1) % self.period
        if not self.index:
            self.action(state)

    def action(self, state):
        pass


class PeriodicReset(PeriodicActionPlugin):
    def action(self, state):
        for edge in state.graph.edges:
            state.graph.edges[edge]['pheromone'] = 1


class PheromoneFlip(PeriodicActionPlugin):
    def action(self, state):
        data = []
        for edge in state.graph.edges.values():
            datum = edge['pheromone'], edge
            data.append(datum)
        levels, edges = zip(*data)
        for edge, level in zip(edges, reversed(levels)):
            edge['pheromone'] = level


class TimerPlugin(SolverPlugin):
    def initialize(self, solver):
        super().initialize(solver)
        self.start_time = None
        self.finsih_time = None
        self.duration = None

    def on_start(self, state):
        self.start_time = time.time()

    def on_finish(self, state):
        self.finsih_time = time.time()
        self.duration = self.finsih_time - self.start_time
        print(f'Total time: {self.duration} seconds')


class DarwinPlugin(SolverPlugin):
    def __init__(self, sigma=.1):
        self.sigma = sigma

    def on_start(self, state):
        size = len(state.ants)
        self.alpha = sum(ant.alpha for ant in state.ants) / size
        self.beta = sum(ant.beta for ant in state.ants) / size

    def on_iteration(self, state):
        alpha = (self.alpha + state.best.alpha) / 2
        beta = (self.beta + state.best.beta) / 2
        for ant in state.ants:
            ant.alpha = random.gauss(alpha, self.sigma)
            ant.beta = random.gauss(beta, self.sigma)


class EarlyTerminationPlugin(SolverPlugin):
    def on_iteration(self, state):
        if self.should_terminate(state):
            raise StopIteration()

    def should_terminate(self, state):
        raise NotImplementedError()


class ThresholdPlugin(EarlyTerminationPlugin):
    def __init__(self, threshold):
        self.threshold = threshold

    def should_terminate(self, state):
        return state.record.weight <= self.threshold


class TimeLimitPlugin(EarlyTerminationPlugin):
    def __init__(self, seconds):
        self.limit = seconds

    def on_start(self, state):
        self.start_time = time.time()

    def should_terminate(self, state):
        duration = time.time() - self.start_time
        return duration >= self.limit


class EvolutionPlugin(SolverPlugin):

    def on_iteration(self, state):
        survivors = self.trials(state.ants)
        state.ants = self.procreate(survivors)

    def trials(self, ants):
        ants = list(ants)
        n = len(ants)
        h = n // 2
        back_half = ants[h:]
        random.shuffle(back_half)
        ants[h:] = back_half
        for i in range(h):
            if random.random() < i / n:
                j = n - i
                ants[i], ants[j] = ants[j], ants[i]
        return ants[:h]

    def procreate(self, ants):
        next_generation = []
        random.shuffle(ants)
        for ant in ants:
            next_generation.append(self.get_it_on(ant))
            next_generation.append(self.get_it_on(ant))
        return next_generation

    def get_it_on(self, ant):
        sigma = random.gauss(.5, .1)
        alpha = random.gauss(ant.alpha, sigma)
        beta = random.gauss(ant.beta, sigma)
        return Ant(alpha=alpha, beta=beta)


class SelfishGenePlugin(SolverPlugin):
    def on_start(self, state):
        state.ants = [GeneticAnt.from_ant(ant) for ant in state.ants]

    def on_iteration(self, state):
        survivors = self.trials(state.ants)
        state.ants = self.procreate(survivors)

    def trials(self, ants):
        ants = list(ants)
        n = len(ants)
        h = n // 2
        back_half = ants[h:]
        random.shuffle(back_half)
        ants[h:] = back_half
        for i in range(h):
            if random.random() < i / n:
                j = n - i
                ants[i], ants[j] = ants[j], ants[i]
        return ants[:h]

    def pairwise(self, ants):
        return zip(ants[0::2], ants[1::2])

    def procreate(self, ants):
        next_generation = []
        random.shuffle(ants)
        for parents in self.pairwise(ants):
            next_generation.append(self.get_it_on(parents))
            next_generation.append(self.get_it_on(parents))
            next_generation.append(self.get_it_on(parents))
            next_generation.append(self.get_it_on(parents))
        return next_generation

    def get_it_on(self, parents):
        a1, b1 = parents[0].get_gamete_dna()
        a2, b2 = parents[1].get_gamete_dna()
        a3 = a1 + a2
        b3 = b1 + b2
        pA = a3.count('A') * .5
        pB = b3.count('B') * .5
        alphas = list(p.alpha for p in parents)
        betas = list(p.beta for p in parents)
        if 0 < pA < 1:
            a = random.choice(alphas)
        elif pA == 1:
            a = max(alphas)
        else:
            a = min(alphas)

        if 0 < pB < 1:
            b = random.choice(betas)
        elif pA == 1:
            b = max(betas)
        else:
            b = min(betas)

        a = random.gauss(a, 0.01)
        b = random.gauss(b, 0.01)
        return GeneticAnt(a, b, dna=a3 + b3)


class StatRecorder(SolverPlugin):
    def __init__(self):
        self.stats = collections.defaultdict(list)
        self.data = {'solutions': set()}

    def on_start(self, state):
        levels = [edge['pheromone'] for edge in state.graph.edges.values()]
        num_edges = len(levels)
        total_pheromone = sum(levels)

        stats = {
            'pheromone_levels': levels,
            'total_pheromone': total_pheromone,
            'edge_pheromone': {
                'min': min(levels),
                'max': max(levels),
                'avg': total_pheromone / num_edges,
            },
            'solutions': {
                'best': None,
                'worst': None,
                'avg': None,
                'global_best': None,
            },
            'unique_solutions': {
                'total': len(self.data['solutions']),
                'iteration': 0,
                'new': 0,
            }
        }
        self.pump(stats)

    def on_iteration(self, state):
        levels = [edge['pheromone'] for edge in state.graph.edges.values()]
        distances = [solution.weight for solution in state.solutions]

        solutions = set(state.solutions)
        solutions_seen = self.data['solutions']

        old_count = len(solutions_seen)
        solutions_seen.update(solutions)
        num_new_solutions = len(solutions_seen) - old_count

        num_edges = len(levels)
        num_ants = len(distances)
        total_pheromone = sum(levels)

        stats = {
            'pheromone_levels': levels,
            'total_pheromone': total_pheromone,
            'edge_pheromone': {
                'min': min(levels),
                'max': max(levels),
                'avg': total_pheromone / num_edges,
            },
            'solutions': {
                'best': min(distances),
                'worst': max(distances),
                'avg': sum(distances) / num_ants,
                'global_best': state.best.weight,
            },
            'unique_solutions': {
                'total': len(self.data['solutions']),
                'iteration': len(solutions),
                'new': num_new_solutions,
            }
        }
        self.pump(stats)

    def on_finish(self, state):
        self.plot()

    def pump(self, stats):
        for stat, data in stats.items():
            self.stats[stat].append(data)

    def plot(self):
        plt.figure()
        plt.title('Solutions (stats)')
        self.plot_solutions()

        plt.figure()
        plt.title('Edge Pheromone (levels)')
        self.plot_pheromone_levels(legend=False)

        plt.figure()
        plt.title('Edge Pheromone (stats)')
        self.plot_edge_pheromone()

        plt.figure()
        plt.title('Solutions (uniqueness)')
        self.plot_unique_solutions()

        plt.show()

    def _plot(self, stat, ax=None, **kwargs):
        data = self._extract_and_process(stat)
        data.plot(ax=ax or plt.gca(), **kwargs)

    def __getattr__(self, name):
        if name.startswith('plot_'):
            __, stat = name.split('_', 1)
            return functools.partial(self._plot, stat)
        raise AttributeError(name)

    def _extract_and_process(self, stat):
        extractor = getattr(self, f'extract_{stat}', lambda: self.stats[stat])
        processor = getattr(self, f'process_{stat}', lambda d: pd.DataFrame(d))
        return processor(extractor())

    def extract_ant_distances(self):
        iterations = []
        for distances in self.stats['ant_distances']:
            if all(d is not None for d in distances):
                distances = list(sorted(distances))
            iterations.append(distances)
        return iterations


def avg(values):
    return sum(values) / len(values)


class StatsdPlugin(SolverPlugin):
    def __init__(self, *args, prefix='pants', **kwargs):
        prefix += '.{}'.format(int(time.time()))
        self.client = statsd.StatsClient(*args, prefix=prefix, **kwargs)

    def on_iteration(self, state):
        unique_edges = set(tuple(sorted(edge)) for edge in state.graph.edges)
        with self.client.pipeline() as pipe:
            for u, v in unique_edges:
                key = 'pheromone.{}-{}'.format(u, v)
                pipe.gauge(key, state.graph.edges[u, v]['pheromone'])

            distances = [s.weight for s in state.solutions]
            pipe.gauge('solutions.best', min(distances))
            pipe.gauge('solutions.avg', avg(distances))
            pipe.gauge('solutions.worst', max(distances))
            pipe.gauge('solutions.record', state.record.weight)

            for solution in state.solutions:
                pipe.set('solutions.unique', solution)
