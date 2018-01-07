import functools
import itertools
import bisect
import random

from . import exceptions


@functools.total_ordering
class Ant:

    _uid = 0

    def __init__(self, world=None, alpha=1, beta=3, q=1):
        self.alpha = alpha
        self.beta = beta
        self._q = q

        self._id = self.__class__._uid
        self.__class__._uid += 1

        self._is_finalized = False
        self._visited_nodes = set()
        self.current_node = None
        self.path = []
        self._distance = 0
        self.world = world

    def __eq__(self, other):
        if self.world != other.world:
            return NotImplemented
        return self.distance == other.distance

    def __lt__(self, other):
        if self.world != other.world:
            return NotImplemented
        return self.distance < other.distance

    @property
    def q(self):
        factor = self.world.total_weight if self.is_bound else 1
        return factor * self._q

    @q.setter
    def q(self, q):
        self._q = q

    @property
    def pheromone(self):
        return self.q / (self.distance or 1)

    @property
    def is_bound(self):
        return self.world is not None

    @property
    def distance(self):
        return self._distance

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, world):
        self._world = world
        self.reset()

    @property
    def solution_id(self):
        if not self._is_finalized:
            return None
        if not self._solution_id:
            nodes = list(edge.start for edge in self.path)
            first = min(nodes)
            index = nodes.index(first)
            self._solution_id = tuple(nodes[index:] + nodes[:index])
        return self._solution_id

    def reset(self):
        self._is_finalized = False
        self._solution_id = None
        self._distance = 0
        self.current_node = None
        self._visited_nodes = set()
        self.path = []
        if self.is_bound:
            self.current_node = self.get_start_node()
            self._visited_nodes.add(self.current_node)

    def _get_final_move(self):
        start = self.path[-1].end
        end = self.path[0].start
        return self.world.get_edge(start, end)

    def move(self):
        moves = self.get_moves()
        if not moves:
            if not self._is_finalized:
                chosen_move = self._get_final_move()
                self._is_finalized = True
            else:
                raise exceptions.ZeroMovesError(self)
        elif len(moves) == 1:
            chosen_move = moves[0]
        else:
            chosen_move = self.choose_move(moves)
        self.make_move(chosen_move)
        return chosen_move

    def try_move(self):
        try:
            self.move()
        except exceptions.ZeroMovesError:
            return False
        else:
            return True

    def can_move(self):
        return bool(self.get_moves()) and self._is_finalized

    def get_moves(self):
        return self.world.get_edges_from(self.current_node,
                                         not_to=self._visited_nodes)

    def choose_move(self, choices):
        weights = self.weigh_moves(choices)
        return self.choose_weighted_move(choices, weights)

    def weigh_moves(self, choices):
        weights = []
        for edge in choices:
            weights.append(self.weigh_move(edge))
        return weights

    def choose_weighted_move(self, choices, weights):
        # use a weighted probability
        total = sum(weights)
        cumdist = list(itertools.accumulate(weights)) + [total]
        index = bisect.bisect(cumdist, random.random() * total)
        return choices[index]

    def weigh_move(self, edge):
        pre = 1 / (edge.weight or 1)
        post = edge.pheromone.amount
        weight = post ** self.alpha * pre ** self.beta
        return weight

    def make_move(self, edge):
        self._distance += edge.weight
        self._visited_nodes.add(edge.end)
        self.path.append(edge)
        self.current_node = edge.end

    def get_start_node(self):
        return random.choice(self.world.nodes)


class AntFarm:
    def __init__(self, cls=Ant):
        self.cls = cls

    def breed(self, count=10):
        ants = []
        for index in range(count):
            ant = self.create_ant(_index=index, _count=count)
            ants.append(ant)
        return ants

    def get_ant_kwargs(self, index=None, count=None):
        return {}

    def create_ant(self, _index=None, _count=None, **overrides):
        kwargs = self.get_ant_kwargs(index=_index, count=_count)
        kwargs.update(overrides)
        return self.cls(**kwargs)


class SpecificAntFarm(AntFarm):
    def __init__(self, alpha=1, beta=3, q=1, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
        self.beta = beta
        self.q = q

    def get_ant_kwargs(self, **kwargs):
        return {
            'alpha': self.alpha,
            'beta': self.beta,
            'q': self.q,
        }


class RandomAntFarm(AntFarm):
    def __init__(self, min_alpha=.5, max_alpha=1, min_beta=1, max_beta=3,
                 **kwargs):
        super().__init__(**kwargs)
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.min_beta = min_beta
        self.max_beta = max_beta

    def get_value(self, param):
        low = getattr(self, 'min_{}'.format(param))
        high = getattr(self, 'max_{}'.format(param))
        return (high - low) * random.random() + low

    def get_ant_kwargs(self, **kwargs):
        return {
            'alpha': self.get_value('alpha'),
            'beta': self.get_value('beta'),
        }


class Colony:
    def __init__(self, world, ants):
        self.ants = ants
        self.world = world

    @property
    def world(self):
        return self._world

    @world.setter
    def world(self, world):
        self._world = world
        for ant in self.ants:
            ant.world = world

    def get_best_ant(self):
        return sorted(self.ants)[0]

    def reset_ants(self):
        for ant in self.ants:
            ant.reset()

    def aco(self):
        self.reset_ants()
        self.find_solutions()
        self.do_global_update()
        return self.get_best_ant()

    def find_solutions(self):
        ants_working = True
        while ants_working:
            ants_working = 0
            for ant in self.ants:
                if ant.try_move():
                    ants_working += 1

    def do_global_update(self):
        ants = sorted(self.ants)[:2]
        for ant in ants:
            p = ant.pheromone
            for edge in ant.path:
                old_amount = edge.pheromone.amount
                amount = (1 - edge.pheromone.rho) * old_amount + p
                edge.pheromone.amount = amount
