# -*- coding: utf-8 -*-
import collections
import random
import time
import os
import networkx as nx
import matplotlib.pyplot as plt

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


class InitialSolution(SolverPlugin):

    def __init__(self, q=1):
        super().__init__()
        self.q = q

    def on_start(self, state):
        for edge in state.graph.edges:
            if state.graph.edges[edge]['weight'] == 0:
                state.graph.edges[edge]['weight'] = 1e100
            state.graph.edges[edge]['pheromone'] = self.q / state.graph.edges[edge]['weight']


class EliteTracer(SolverPlugin):

    def __init__(self, factor=1):
        super().__init__(factor=factor)
        self.factor = factor

    def on_iteration(self, state):
        state.best.trace(self.solver.q * self.factor)


class MaxMinPheromoneRestrict(SolverPlugin):

    def __init__(self, p_best=0.05, save_path='.', leading=''):
        super().__init__()
        self.p_best = p_best
        self.save_path = save_path
        self.leading = leading
        self.tau_maxs = []
        self.tau_mins = []
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

    def on_iteration(self, state):
        record_cost = state.record.cost
        rho = state.rho
        n = state.graph.number_of_nodes()

        tau_max = (1 / rho) * (1 / record_cost)
        tau_min = (tau_max * (1 - self.p_best ** (1 / n))) / ((n / 2 - 1) * (self.p_best ** (1 / n)))

        for edge in state.graph.edges():
            p = state.graph.edges[edge]['pheromone']
            p = min(tau_max, max(tau_min, p))
            state.graph.edges[edge]['pheromone'] = p

        self.tau_maxs.append(tau_max)
        self.tau_mins.append(tau_min)

    def draw(self, state):
        fig = plt.figure(dpi=200)
        x = list(range(len(self.tau_maxs)))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x, self.tau_mins, label='min')
        ax.plot(x, self.tau_maxs, label='max')
        ax.set_title('MaxMin Pheromone')
        ax.legend()
        fig.show()
        fig.savefig(os.path.join(self.save_path, self.leading + '_maxmin_pheromone.png'))

    def on_finish(self, state):
        super().on_finish(state)
        self.draw(state)


class Opt2Swap(SolverPlugin):
    def __init__(self, opt2=10):
        super().__init__()
        self.opt2 = opt2
        self.swaps = 0

    def on_before(self, state):
        solutions = state.solutions
        graph = state.graph
        n = len(graph.nodes)

        for s in solutions:
            while True:
                x, y = random.randint(0, n - 1), random.randint(0, n - 1)
                if x > y:
                    x, y = y, x
                if x != y:
                    break
            dist_a = graph.edges[s.nodes[x], s.nodes[x + 1]]['weight']
            dist_b = graph.edges[s.nodes[y], s.nodes[(y + 1) % n]]['weight']
            dist_c = graph.edges[s.nodes[x], s.nodes[y]]['weight']
            dist_d = graph.edges[s.nodes[x + 1], s.nodes[(y + 1) % n]]['weight']
            if dist_a + dist_b > dist_c + dist_d:
                s.nodes[x + 1: y + 1] = reversed(s.nodes[x + 1: y + 1])
                s.cost += dist_c + dist_d - dist_a - dist_b
                s.reconstruct()
                self.swaps += 1


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

    def __init__(self, period=50):
        super().__init__(period=period)

    def action(self, state):
        for edge in state.graph.edges:
            state.graph.edges[edge]['pheromone'] = 0


class PheromoneFlip(PeriodicActionPlugin):

    def __init__(self, period=50):
        super().__init__(period=period)

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


class DrawGraph(SolverPlugin):
    def __init__(self, problem, save_path='.', leading='', is_iteration=False, is_finish=True, is_save=False):
        super().__init__()
        self.pos = problem.display_data or problem.node_coords
        self.save_path = save_path
        self.leading = leading
        self.is_iteration = is_iteration
        self.is_finish = is_finish
        self.is_save = is_save
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

    def on_iteration(self, state):
        if self.is_iteration:
            self.draw(state)

    def on_finish(self, state):
        if self.is_finish:
            self.draw(state)
        if self.is_save:
            self.save(state)

    def draw(self, state):
        plt.figure()
        _, ax = plt.subplots()
        nx.draw_networkx_nodes(state.graph, pos=self.pos, ax=ax)
        nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=state.record.path, arrows=False)
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        plt.show()

    def save(self, state):
        plt.figure(dpi=200)
        _, ax = plt.subplots()
        nx.draw_networkx_nodes(state.graph, pos=self.pos, ax=ax)
        nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=state.record.path, arrows=False)
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        plt.savefig(os.path.join(self.save_path, self.leading + '_graph_record.png'))


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
                'global_best': state.record.cost,
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
