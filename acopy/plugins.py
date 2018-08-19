# -*- coding: utf-8 -*-
import collections
import math
import random
import time

from .solvers import SolverPlugin


class Printout(SolverPlugin):

    _ROW = '{:<10} {:<20} {}'

    def initialize(self, solver):
        super().initialize(solver)
        self.iteration = 0

    def on_start(self, state):
        self.iteration = 0
        print(f'Using {state.gen_size} ants from {state.colony}')
        print(f'Performing {state.limit} iterations:')
        print(self._ROW.format('Iteration', 'Cost', 'Solution'))

    def on_iteration(self, state):
        self.iteration += 1
        line = self._ROW.format(self.iteration, state.best.cost,
                                state.best.get_easy_id())
        print(line, end='\n' if state.is_new_record else '\r')

    def on_finish(self, state):
        print('Done' + ' ' * (32 + 2 * len(state.graph)))


class EliteTracer(SolverPlugin):

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

    def action(self, state):
        for edge in state.graph.edges:
            state.graph.edges[edge]['pheromone'] = 0


class PheromoneFlip(PeriodicActionPlugin):

    def action(self, state):
        data = []
        for edge in state.graph.edges.values():
            datum = edge['pheromone'], edge
            data.append(datum)
        levels, edges = zip(*data)
        for edge, level in zip(edges, reversed(levels)):
            edge['pheromone'] = level


class Timer(SolverPlugin):

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


class Darwin(SolverPlugin):

    def __init__(self, sigma=.1):
        super().__init__(sigma=sigma)
        self.sigma = sigma

    def on_start(self, state):
        size = len(state.ants)
        self.alpha = sum(ant.alpha for ant in state.ants) / size
        self.beta = sum(ant.beta for ant in state.ants) / size

    def on_iteration(self, state):
        alpha = (self.alpha + state.best.ant.alpha) / 2
        beta = (self.beta + state.best.ant.beta) / 2
        for ant in state.ants:
            ant.alpha = random.gauss(alpha, self.sigma)
            ant.beta = random.gauss(beta, self.sigma)


class EarlyTerminationPlugin(SolverPlugin):
    def on_iteration(self, state):
        if self.should_terminate(state):
            raise StopIteration()

    def should_terminate(self, state):
        raise NotImplementedError()


class Threshold(EarlyTerminationPlugin):

    def __init__(self, threshold):
        super().__init__(threshold=threshold)
        self.threshold = threshold

    def should_terminate(self, state):
        return state.record.cost <= self.threshold


class TimeLimit(EarlyTerminationPlugin):

    def __init__(self, seconds):
        super().__init__(seconds=seconds)
        self.limit = seconds

    def on_start(self, state):
        self.start_time = time.time()

    def should_terminate(self, state):
        duration = time.time() - self.start_time
        return duration >= self.limit


class StatsRecorder(SolverPlugin):

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
        distances = [solution.cost for solution in state.solutions]

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
                'global_best': state.best.cost,
            },
            'unique_solutions': {
                'total': len(self.data['solutions']),
                'iteration': len(solutions),
                'new': num_new_solutions,
            }
        }
        self.pump(stats)

    def pump(self, stats):
        for stat, data in stats.items():
            self.stats[stat].append(data)
