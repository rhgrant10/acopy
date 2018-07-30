import sys
import functools
import textwrap
import collections


@functools.total_ordering
class Solution:
    def __init__(self, graph, start, ant=None):
        self.graph = graph
        self.start = start
        self.ant = ant
        self.current = start
        self.weight = 0
        self.path = []
        self.nodes = [start]
        self.visited = set(self.nodes)

    def __iter__(self):
        return iter(self.path)

    def __eq__(self, other):
        return self.weight == other.weight

    def __lt__(self, other):
        return self.weight < other.weight

    def __contains__(self, node):
        return node in self.visited or node == self.current

    def __repr__(self):
        easy_id = ''.join(str(n) for n in self.get_id())
        return '{} ({}, {})'.format(easy_id, self.weight, self.ant)

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
        self.record = None
        self.previous_record = None
        self.is_new_record = False
        self.best = None

    @property
    def best(self):
        return self._best

    @best.setter
    def best(self, best):
        self.is_new_record = self.record is None or best < self.record
        if self.is_new_record:
            self.old_record = self.record
            self.record = best
        self._best = best


class Solver:
    def __init__(self, rho=.03, q=1, top=2, plugins=None):
        self.rho = rho
        self.q = q
        self.top = top
        self.plugins = collections.OrderedDict()
        if plugins:
            self.add_plugins(*plugins)

    def __repr__(self):
        return (f'{self.__class__.__name__}(rho={self.rho}, q={self.q}, '
                f'top={self.top})')

    def __str__(self):
        plugin_reprs = '\n'.join([repr(p) for p in self.get_plugins()])
        plugins = textwrap.indent(plugin_reprs, prefix='  ')
        return f'{repr(self)}\n{plugins}'

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

        def loops(limit):
            if limit is not None:
                return range(limit)

            def forever():
                i = 0
                while True:
                    yield i
                    i += 1
            return forever()

        for __ in loops(limit):
            # find solutions and update the graph pheromone accordingly
            solutions = self.find_solutions(state.graph, state.ants)
            data = list(zip(solutions, range(len(state.ants)), state.ants))
            data.sort()
            solutions, __, ants = zip(*data)
            state.solutions = solutions
            state.ants = ants
            self.global_update(state)

            # yield increasingly better solutions
            state.best = state.solutions[0]
            if state.is_new_record:
                yield state.record

            # call iteration hook for all plugins
            if self._call_plugins('iteration', state=state):
                break

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
            self.plugins[plugin.name] = plugin

    def get_plugins(self):
        return self.plugins.values()

    def _call_plugins(self, hook, **kwargs):
        should_stop = False
        for plugin in self.get_plugins():
            try:
                plugin(hook, **kwargs)
            except StopIteration:
                should_stop = True
        return should_stop


class SolverPlugin:
    name = 'plugin'

    def __init__(self, **kwargs):
        self._params = kwargs

    def __repr__(self):
        params = ', '.join(f'{k}={v}'for k, v in self._params.items())
        return f'{self.name}[{params}]'

    def __call__(self, hook, **kwargs):
        return getattr(self, f'on_{hook}')(**kwargs)

    def initialize(self, solver):
        self.solver = solver

    def on_start(self, state):
        pass

    def on_iteration(self, state):
        pass

    def on_finish(self, state):
        pass
