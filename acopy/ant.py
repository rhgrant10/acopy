# -*- coding: utf-8 -*-
import sys
import itertools
import bisect
import random

from .utils import positive
from .solvers import Solution


class Ant:
    """An ant.

    Ants explore a graph, using alpha and beta to guide their decision making
    process when choosing which edge to travel next.

    :param float alpha: how much pheromone matters
    :param float beta: how much distance matters
    """

    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    @property
    def alpha(self):
        """How much pheromone matters. Always kept greater than zero."""
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = positive(value)

    @property
    def beta(self):
        """How much distance matters. Always kept greater than zero."""
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = positive(value)

    def __repr__(self):
        return f'Ant(alpha={self.alpha}, beta={self.beta})'

    def tour(self, graph):
        """Find a solution to the given graph.

        :param graph: the graph to solve
        :type graph: :class:`networkx.Graph`
        :return: one solution
        :rtype: :class:`~acopy.solvers.Solution`
        """
        solution = self.initialize_solution(graph)
        unvisited = self.get_unvisited_nodes(graph, solution)
        while unvisited:
            node = self.choose_destination(graph, solution.current, unvisited)
            solution.add_node(node)
            unvisited.remove(node)
        solution.close()
        return solution

    def initialize_solution(self, graph):
        """Return a newly initialized solution for the given graph.

        :param graph: the graph to solve
        :type graph: :class:`networkx.Graph`
        :return: intialized solution
        :rtype: :class:`~acopy.solvers.Solution`
        """
        start = self.get_starting_node(graph)
        return Solution(graph, start, ant=self)

    def get_starting_node(self, graph):
        """Return a starting node for an ant.

        :param graph: the graph being solved
        :type graph: :class:`networkx.Graph`
        :return: node
        """
        return random.choice(list(graph.nodes))

    def get_unvisited_nodes(self, graph, solution):
        """Return the unvisited nodes.

        :param graph: the graph being solved
        :type graph: :class:`networkx.Graph`
        :param solution: in progress solution
        :type solution: :class:`~acopy.solvers.Solution`
        :return: unvisited nodes
        :rtype: list
        """
        nodes = []
        for node in graph[solution.current]:
            if node not in solution:
                nodes.append(node)
        return nodes

    def choose_destination(self, graph, current, unvisited):
        """Return the next node.

        :param graph: the graph being solved
        :type graph: :class:`networkx.Graph`
        :param current: starting node
        :param list unvisited: available nodes
        :return: chosen edge
        """
        if len(unvisited) == 1:
            return unvisited[0]
        scores = self.get_scores(graph, current, unvisited)
        return self.choose_node(unvisited, scores)

    def get_scores(self, graph, current, destinations):
        """Return scores for the given destinations.

        :param graph: the graph being solved
        :type graph: :class:`networkx.Graph`
        :param current: the node from which to score the destinations
        :param list destinations: available, unvisited nodes
        :return: scores
        :rtype: list
        """
        scores = []
        for node in destinations:
            edge = graph.edges[current, node]
            score = self.score_edge(edge)
            scores.append(score)
        return scores

    def choose_node(self, choices, scores):
        """Return one of the choices.

        Note that ``scores[i]`` corresponds to ``choices[i]``.

        :param list choices: the unvisited nodes
        :param list scores: the scores for the given choices
        :return: one of the choices
        """
        total = sum(scores)
        cumdist = list(itertools.accumulate(scores)) + [total]
        index = bisect.bisect(cumdist, random.random() * total)
        return choices[min(index, len(choices) - 1)]

    def score_edge(self, edge):
        """Return the score for the given edge.

        :param dict edge: the edge data
        :return: score
        :rtype: float
        """
        weight = edge.get('weight', 1)
        if weight == 0:
            return sys.float_info.max
        pre = 1 / weight
        post = edge['pheromone']
        return post ** self.alpha * pre ** self.beta


class Colony:
    """Colony of ants.

    Effectively this is a source of :class:`~acopy.ant.Ant` for a
    :class:`~acopy.solvers.Solver`.

    :param float alpha: relative factor for edge weight
    :param float beta: relative factor for edge pheromone
    """

    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def __repr__(self):
        return (f'{self.__class__.__name__}(alpha={self.alpha}, '
                f'beta={self.beta})')

    def get_ants(self, count):
        """Return the requested number of :class:`~acopy.ant.Ant` s.

        :param int count: number of ants to return
        :rtype: list
        """
        return [Ant(**vars(self)) for __ in range(count)]
