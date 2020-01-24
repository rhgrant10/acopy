import sys
import itertools
import bisect
import random

from .utils import positive
from .solvers import Solution
from .ant import Ant


class RandomAnt(Ant):

    def __init__(self, alpha=1, beta=3, q_0=0.2):
        super().__init__(alpha, beta)
        self.q_0 = q_0

    def choose_node(self, choices, scores):
        total = sum(scores)
        cumdist = list(itertools.accumulate(scores)) + [total]
        q = random.random()
        if q < self.q_0:
            index = random.randint(0, len(choices) - 1)
        else:
            index = bisect.bisect(cumdist, random.random() * total)
        return choices[min(index, len(choices) - 1)]
