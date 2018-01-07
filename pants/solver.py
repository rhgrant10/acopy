import functools

from .ant import Colony


@functools.total_ordering
class Solution:
    def __init__(self, ant):
        self.edges = ant.path
        self.nodes = ant.solution_id
        self.alpha = ant.alpha
        self.beta = ant.beta
        self.q = ant.q
        self.weight = sum(edge.weight for edge in self.edges)

    def __eq__(self, other):
        return self.weight == other.weight

    def __lt__(self, other):
        return self.weight < other.weight

    def __iter__(self):
        return iter(self.edges)

    def retrace(self, factor=1):
        amount = self.q * factor
        for edge in self:
            edge.pheromone.amount += amount


class Solver:
    def __init__(self, farm, limit=100):
        self.farm = farm
        self.limit = limit
        self.plugins = []

    def get_colony(self, world, size=None):
        if not size:
            size = len(world.nodes)
        ants = self.farm.breed(count=size)

        # FIXME: Solver should not directly depend on Colony
        # What to do? We could remove get_colony and accept a colony as a
        # parameter to solve. We could reverse this whole bitch and instead,
        # have colony.get_solver(limit=...). That way, each solver would be
        # naturally bound to both a colony and a world, which makes tracking
        # global best for a particular solver over multiple calls to
        # get_solutions a cinch (thumbsup)
        return Colony(world, ants)

    def solve(self, world, size=None):
        best = None
        for solution in self.get_solutions(world, size=size):
            best = solution
        return best

    def get_solutions(self, world, size=None):
        global_best = None
        colony = self.get_colony(world, size=size)
        self._call_plugins('start', colony)
        for i in range(self.limit):
            best_ant = Solution(colony.aco())
            is_new_best = global_best is None or best_ant < global_best
            if is_new_best:
                global_best = best_ant
                yield global_best
            self._call_plugins('iteration', colony, global_best, is_new_best)
        self._call_plugins('finish', colony, global_best)

    def add_plugin(self, plugin):
        self.add_plugins(plugin)

    def add_plugins(self, *plugins):
        for plugin in plugins:
            plugin.initialize(self)
        self.plugins.extend(plugins)

    def _call_plugins(self, hook, *args, **kwargs):
        for plugin in self.plugins:
            plugin(hook, *args, **kwargs)


class SolverPlugin:
    def __call__(self, hook, *args, **kwargs):
        return getattr(self, f'on_{hook}')(*args, **kwargs)

    def initialize(self, solver):
        pass

    def on_start(self, colony):
        pass

    def on_iteration(self, colony, global_best, is_new_best):
        pass

    def on_finish(self, colony, global_best):
        pass
