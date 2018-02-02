import sys
import functools


@functools.total_ordering
class Solution:
    def __init__(self, graph, start, alpha=None, beta=None):
        self.graph = graph
        self.start = start
        self.alpha = alpha
        self.beta = beta
        self.current = start
        self.weight = 0
        self.path = []
        self.nodes = [start]
        self.visited = set(self.nodes)
        self._size = max(len(str(n)) for n in self.graph.nodes)

    def __iter__(self):
        return iter(self.path)

    def __eq__(self, other):
        return self.weight == other.weight

    def __lt__(self, other):
        return self.weight < other.weight

    def __contains__(self, node):
        return node in self.visited or node == self.current

    def __repr__(self):
        def space(n):
            return '{: >{size}s}'.format(n, size=self._size)
        easy_id = ''.join(space(n) for n in self.get_id())
        return '{} ({}, a={}, b={})'.format(easy_id, self.weight, self.alpha,
                                            self.beta)

    def __hash__(self):
        return hash(self.get_id())

    def get_id(self):
        first = min(self.nodes)
        index = self.nodes.index(first)
        return tuple(self.nodes[index:] + self.nodes[:index])

    def add_node(self, node):
        self.nodes.append(node)
        self.visited.add(node)
        self._add_node(node)

    def close(self):
        self._add_node(self.start)

    def _add_node(self, node):
        edge = self.current, node
        data = self.graph.edges[edge]
        self.path.append(edge)
        self.weight += data['weight']
        self.current = node

    def trace(self, q, rho=0):
        amount = q / self.weight
        for edge in self.path:
            self.graph.edges[edge]['pheromone'] += amount
            self.graph.edges[edge]['pheromone'] *= 1 - rho
            if not self.graph.edges[edge]['pheromone']:
                self.graph.edges[edge]['pheromone'] = sys.float_info.min


class State:
    def __init__(self, graph, ants, limit, gen_size):
        self.graph = graph
        self.ants = ants
        self.limit = limit
        self.gen_size = gen_size
        self.solutions = None
        self.best = None


class Solver:
    def __init__(self, rho=.03, q=1, top=2, plugins=None):
        self.rho = rho
        self.q = q
        self.top = top
        self.plugins = []
        if plugins:
            self.add_plugins(*plugins)

    def solve(self, *args, **kwargs):
        best = None
        for solution in self.optimize(*args, **kwargs):
            best = solution
        return best

    def optimize(self, graph, colony, gen_size=None, limit=100):
        # initialize the colony of ants and the graph
        gen_size = gen_size or len(graph.nodes)
        ants = colony.get_ants(gen_size)
        for u, v in graph.edges:
            graph.edges[u, v].setdefault('pheromone', 1)

        state = State(graph=graph, ants=ants, limit=limit, gen_size=gen_size)

        # call start hook for all plugins
        self._call_plugins('start', state=state)

        for __ in range(limit):
            # find solutions and update the graph pheromone accordingly
            state.solutions = self.find_solutions(state.graph, state.ants)
            state.solutions.sort()
            self.global_update(state)

            # yield increasingly better solutions
            is_new_best = state.best is None or state.solutions[0] < state.best
            if is_new_best:
                state.best = state.solutions[0]
                yield state.best

            # call iteration hook for all plugins
            self._call_plugins('iteration', state=state,
                               is_new_best=is_new_best)

        # call finish hook for all plugins
        self._call_plugins('finish', state=state)

    def find_solutions(self, graph, ants):
        return [ant.tour(graph) for ant in ants]

    def global_update(self, state):
        for edge in state.graph.edges:
            amount = 0
            for solution in state.solutions[:self.top]:
                if edge in solution.path:
                    amount += self.q / solution.weight
            p = state.graph.edges[edge]['pheromone']
            state.graph.edges[edge]['pheromone'] = (1 - self.rho) * p + amount

    def add_plugin(self, plugin):
        self.add_plugins(plugin)

    def add_plugins(self, *plugins):
        for plugin in plugins:
            plugin.initialize(self)
        self.plugins.extend(plugins)

    def _call_plugins(self, hook, **kwargs):
        for plugin in self.plugins:
            plugin(hook, **kwargs)


class IncreasingSolver(Solver):
    def global_update(self, state):
        for solution in state.solutions[:self.top]:
            solution.trace(self.q, rho=self.rho)


class SolverPlugin:
    def __call__(self, hook, **kwargs):
        return getattr(self, f'on_{hook}')(**kwargs)

    def initialize(self, solver):
        self.solver = solver

    def on_start(self, state):
        pass

    def on_iteration(self, state, is_new_best):
        pass

    def on_finish(self, state):
        pass
