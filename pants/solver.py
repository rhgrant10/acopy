import sys
import functools


@functools.total_ordering
class Solution:
    def __init__(self, graph, start):
        self.graph = graph
        self.path = []
        self.current = self.start = start
        self.weight = 0
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
        return '{} ({})'.format(easy_id, self.weight)

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

        # call start hook for all plugins
        self._call_plugins('start', graph=graph, ants=ants, gen_size=gen_size,
                           limit=limit)

        best = None
        for __ in range(limit):
            # find solutions and update the graph pheromone accordingly
            solutions = self.find_solutions(graph, ants)
            self.global_update(graph, solutions)

            # yield increasingly better solutions
            is_new_best = best is None or solutions[0] < best
            if is_new_best:
                best = solutions[0]
                yield best

            # call iteration hook for all plugins
            self._call_plugins('iteration', graph=graph, solutions=solutions,
                               best=best, is_new_best=is_new_best)

        # call finish hook for all plugins
        self._call_plugins('finish', graph=graph, solutions=solutions,
                           best=best)

    def find_solutions(self, graph, ants):
        return [ant.tour(graph) for ant in ants]

    def global_update(self, graph, solutions):
        for solution in sorted(solutions)[:self.top]:
            solution.trace(self.q, rho=self.rho)

    def add_plugin(self, plugin):
        self.add_plugins(plugin)

    def add_plugins(self, *plugins):
        for plugin in plugins:
            plugin.initialize(self)
        self.plugins.extend(plugins)

    def _call_plugins(self, hook, **kwargs):
        for plugin in self.plugins:
            plugin(hook, **kwargs)


class SolverPlugin:
    def __call__(self, hook, **kwargs):
        return getattr(self, f'on_{hook}')(**kwargs)

    def initialize(self, solver):
        self.solver = solver

    def on_start(self, graph, ants, gen_size, limit):
        pass

    def on_iteration(self, graph, solutions, best, is_new_best):
        pass

    def on_finish(self, graph, solutions, best):
        pass
