import sys
import itertools
import bisect
import random

from .utils import positive
from .solvers import Solution
from .ant import Ant


class LocalAnt(Ant):

    def __init__(self, alpha, beta, tau_0, rho):
        super().__init__(alpha, beta)
        self.tau_0 = tau_0
        self.rho = rho

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
            current = solution.current
            node = self.choose_destination(graph, solution.current, unvisited)
            self.local_update(graph, current, node)
            solution.add_node(node)
            unvisited.remove(node)
        solution.close()
        return solution

    def local_update(self, graph, current, next):
        p = graph.edges[current, next]['pheromone']
        p = (1 - self.rho) * p + self.rho * self.tau_0
        graph.edges[current, next]['pheromone'] = p
