import time
import random
import collections
import functools

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError:
    pass

from .solvers import SolverPlugin


class EliteTracer(SolverPlugin):
    name = 'elite'

    def __init__(self, factor=1):
        super().__init__(factor=factor)
        self.factor = factor

    def on_iteration(self, state):
        state.best.trace(self.solver.q * self.factor)


class PeriodicActionPlugin(SolverPlugin):
    def __init__(self, period=50):
        super().__init__(period=period)
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
    name = 'reset'

    def action(self, state):
        for edge in state.graph.edges:
            state.graph.edges[edge]['pheromone'] = 1


class PheromoneFlip(PeriodicActionPlugin):
    name = 'p-flip'

    def action(self, state):
        data = []
        for edge in state.graph.edges.values():
            datum = edge['pheromone'], edge
            data.append(datum)
        levels, edges = zip(*data)
        for edge, level in zip(edges, reversed(levels)):
            edge['pheromone'] = level


class TimerPlugin(SolverPlugin):
    name = 'timer'

    def initialize(self, solver):
        super().initialize(solver)
        self.start_time = None
        self.finish = None
        self.duration = None

    def on_start(self, state):
        self.start_time = time.time()

    def on_finish(self, state):
        self.finish = time.time()
        self.duration = self.finish - self.start_time
        self.time_per_iter = self.duration / state.limit

    def get_report(self):
        return '\n'.join([
            f'Total time: {self.duration} seconds',
            f'Avg iteration time: {self.time_per_iter} seconds',
        ])


class DarwinPlugin(SolverPlugin):
    name = 'darwin'

    def __init__(self, sigma=.1):
        super().__init__(sigma=sigma)
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
    name = 'threshold'

    def __init__(self, threshold):
        super().__init__(threshold=threshold)
        self.threshold = threshold

    def should_terminate(self, state):
        return state.record.weight <= self.threshold


class TimeLimitPlugin(EarlyTerminationPlugin):
    name = 'time-limit'

    def __init__(self, seconds):
        super().__init__(seconds=seconds)
        self.limit = seconds

    def on_start(self, state):
        self.start_time = time.time()

    def should_terminate(self, state):
        duration = time.time() - self.start_time
        return duration >= self.limit


class StatRecorder(SolverPlugin):
    name = 'stats-recorder'

    def __init__(self):
        super().__init__()
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
