import sys
import itertools
import bisect
import random

from .utils import positive
from .solvers import Solution
from .ant import Ant


class EvilAnt(Ant):
    def score_edge(self, edge):
        """Return the score for the given edge.

        :param dict edge: the edge data
        :return: score
        :rtype: float
        """
        weight = edge.get('weight', 1)
        if weight == 0:
            return sys.float_info.max
        pre = weight / 100
        post = edge['pheromone']
        return post ** self.alpha * pre ** self.beta
