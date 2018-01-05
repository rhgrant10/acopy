import random
import itertools
import collections


class Pheromone:
    def __init__(self, amount=.1, t0=None, rho=.8):
        self.t0 = t0 or amount
        self.rho = rho
        self.initial = amount
        self.amount = amount

    def __repr__(self):
        return repr(self.amount)

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        self._amount = max(self.t0, amount)

    def reset(self, amount=None, t0=None, rho=None):
        if t0 is not None:
            self.t0 = t0
        if rho is not None:
            self.rho = rho
        if amount is not None:
            self.amount = amount
        else:
            self.amount = self.amount
        self.initial = self.amount


class Edge:

    default_pool = {}

    def __init__(self, start, end, weight=1, pheromone=1, rho=.5, t0=.01,
                 symmetrical=False, pool=None):
        self.start = start
        self.end = end
        self.weight = weight
        self.symmetrical = symmetrical
        self._vials = self.__class__.default_pool if pool is None else pool
        self.pheromone.reset(amount=pheromone, t0=t0, rho=rho)

    def __repr__(self):
        joiner = '--' if self.symmetrical else '->'
        symbol = '{0.start!r}{1}{0.end!r}'.format(self, joiner)
        template = '<Edge({0}, weight={1.weight}, pheromone={1.pheromone})>'
        return template.format(symbol, self)

    @property
    def vial_id(self):
        keys = [self.start, self.end]
        if self.symmetrical:
            keys.sort()
        keys.append(self.symmetrical)
        return tuple(keys)

    @property
    def pheromone(self):
        try:
            return self._vials[self.vial_id]
        except KeyError:
            vial = Pheromone()
            self._vials[self.vial_id] = vial
            return vial


class World:
    def __init__(self, edges):
        self._nodes = None
        self._edges = None
        self.edge_map = self._create_edge_map(edges)

    @property
    def total_weight(self):
        return sum(e.weight for e in self.edges)

    @property
    def edges(self):
        if self._edges is None:
            edge_lists = [d.values() for d in self.edge_map.values()]
            self._edges = list(itertools.chain(*edge_lists))
        return self._edges

    @property
    def unique_edges(self):
        seen = {}
        for edge in self.edges:
            if edge.vial_id not in seen:
                seen[edge.vial_id] = True
                yield edge

    @property
    def nodes(self):
        if self._nodes is None:
            nodes = set()
            for start, ends in self.edge_map.items():
                nodes.add(start)
                nodes.update(ends.keys())
            self._nodes = list(sorted(nodes))
        return self._nodes

    def _create_edge_map(self, edges):
        edge_map = collections.defaultdict(dict)
        for edge in edges:
            edge_map[edge.start][edge.end] = edge
        return edge_map

    def get_edge(self, start, end):
        edges = self.edge_map[start]
        return edges[end]

    def get_edges_from(self, start, not_to=None):
        edges = self.edge_map[start].values()
        if not_to is None:
            return edges
        return [edge for edge in edges if edge.end not in not_to]

    def get_neighbors(self, start):
        return list(self.edge_map[start].keys())

    def reset_pheromone(self):
        for edge in self.edges:
            edge.pheromone.reset()


class EdgeFactory:
    def __init__(self, cls=Edge, symmetrical=False):
        self.cls = cls
        self.pool = {}
        self.symmetrical = symmetrical

    def create_edge(self, start, end, weight, **overrides):
        kwargs = self.get_edge_kwargs(start, end, weight)
        options = self.get_default_edge_kwargs()
        options.update(kwargs)
        options.update(overrides)
        return self.cls(start, end, weight, **options)

    def get_default_edge_kwargs(self):
        return {'pool': self.pool, 'symmetrical': self.symmetrical}

    def get_edge_kwargs(self, start, end, weight):
        return {}

    def create_edges(self, *edge_list):
        edges = []
        for edge in edge_list:
            edges.append(self.create_edge(*edge))
        return edges


class SpecificEdgeFactory(EdgeFactory):
    def __init__(self, pheromone=1, rho=.1, t0=0.1, **kwargs):
        super().__init__(**kwargs)
        self.pheromone = pheromone
        self.rho = rho
        self.t0 = t0

    def get_edge_kwargs(self, start, end, weight):
        return {
            'pheromone': self.pheromone,
            'rho': self.rho,
            't0': self.t0,
        }


class RandomEdgeFactory(EdgeFactory):
    def __init__(self, min_pheromone=1, max_pheromone=4, min_rho=.2,
                 max_rho=.8, min_t0=.01, max_t0=.01):
        self.min_pheromone = min_pheromone
        self.max_pheromone = max_pheromone
        self.min_rho = min_rho
        self.max_rho = max_rho
        self.min_t0 = min_t0
        self.max_t0 = max_t0

    def get_value(self, param):
        low = getattr(self, 'min_{}'.format(param))
        high = getattr(self, 'max_{}'.format(param))
        return (high - low) * random.random() + low

    def get_edge_kwargs(self):
        return {
            'pheromone': self.get_value('pheromone'),
            'rho': self.get_value('rho'),
            't0': self.get_value('t0'),
        }


class WorldBuilder:
    def __init__(self, cls=World, factory_cls=EdgeFactory):
        self.cls = cls
        self.factory_cls = factory_cls

    def get_edge_factory(self, **kwargs):
        return self.factory_cls(**kwargs)

    def from_edge_list(self, edge_list, symmetrical=False):
        factory = self.get_edge_factory(symmetrical=symmetrical)
        edges = factory.create_edges(*edge_list)
        return self.cls(edges)

    def from_incidence_matrix(self, matrix, symmetrical=False):
        factory = self.get_edge_factory(symmetrical=symmetrical)
        edges = []
        for start, row in enumerate(matrix):
            for end, weight in enumerate(row):
                edge = factory.create_edge(start, end, weight)
                edges.append(edge)
        return self.cls(edges)

    def from_lookup_table(self, table, symmetrical=False):
        factory = self.get_edge_factory(symmetrical=symmetrical)
        edges = []
        for (start, end), weight in table.items():
            edge = factory.create_edge(start, end, weight)
            edges.append(edge)
            if symmetrical:
                edge = factory.create_edge(end, start, weight)
                edges.append(edge)
        return self.cls(edges)
