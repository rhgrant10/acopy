"""
.. module:: ant
    :platform: Linux, Unix, Windows
    :synopsis: Provides functionality for finding each solution step as well
               as representing a complete solution.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""

from .world import World
import itertools
import random
import bisect
import sys

class Ant:
    """
    A single independent finder of solutions to the world.

    """
    uid = 0

    def __init__(self, world, alpha=1, beta=3, start=None):
        """Create a new Ant for the given world.

        :param World world: the world in which to travel
        :param float alpha: the relative importance of pheromone (default=1)
        :param float beta: the relative importance of distance (default=3)
        :param Node start: the starting node (default=None)

        """
        self.uid = Ant.uid
        Ant.uid += 1
        self.world = world
        self.alpha = alpha
        self.beta = beta
        self.start = start
        self.distance = 0
        self.visited = []
        self.unvisited = []
        self.traveled = []

    def initialize(self, start=None):
        """Reset everything so that a new solution can be found.

        :param start: which :class:`Node` to start the next solution from
            (by default, the previous starting node is reused)
        
        """
        if start is None:
            if self.start is None:
                self.start = random.randrange(len(self.world.nodes))
        else:
            self.start = start
        self.distance = 0
        self.visited = [self.start]
        self.unvisited = [n for n in self.world.nodes if n != self.start]
        self.traveled = []
        return self

    def clone(self):
        """Return an identical but new :class:`Ant`.

        Note that unlike copy, this method preserves even the UID of an Ant.

        :returns: a clone
        :rtype: :class:`Ant`

        """
        ant = Ant(self.world, self.alpha, self.beta, self.start)
        ant.uid = self.uid
        ant.visited = self.visited[:]
        ant.unvisited = self.unvisited[:]
        ant.traveled = self.traveled[:]
        ant.distance = self.distance
        return ant


    @property
    def node(self):
        """Node at which the :class:`Ant` currently sits."""
        try:
            return self.visited[-1]
        except IndexError:
            return None

    @property
    def tour(self):
        """Nodes visited by the :class:`Ant` in order."""
        return [self.world.node_data(i) for i in self.visited]

    @property
    def path(self):
        """Edges traveled by the :class:`Ant` in order."""
        return self.traveled

    def __lt__(self, other):
        """Return True if the distance is less than the other distance."""
        return self.distance < other.distance

    def can_move(self):
        """Return True if there are still unvisited nodes."""
        return len(self.traveled) != len(self.visited)

    def move(self):
        """Choose a move and make it."""
        moves = self.remaining_moves()
        move = self.choose_move(moves)
        return self.make_move(move) # returns edge

    def remaining_moves(self):
        """Return the moves that remain to be made."""
        return self.unvisited

    def choose_move(self, choices):
        """Choose a move from all possible moves."""
        if len(choices) == 0:
            return None
        if len(choices) == 1:
            return choices[0]
        weights = []
        for move in choices:
            edge = self.world.edges[self.node, move]
            weights.append(self.weigh(edge))
        total = sum(weights)
        cumdist = list(itertools.accumulate(weights)) + [total]
        return choices[bisect.bisect(cumdist, random.random() * total)]

    def weigh(self, edge):
        """Calculate the weight of a given *edge*."""
        pre = 1 / (edge.length or 1)
        post = edge.pheromone
        return post ** self.alpha * pre ** self.beta

    def make_move(self, move):
        """Move down the given *edge* to it's end node."""
        if move is None:
            if not self.can_move():
                # Last edge already traveled, so do nothing.
                return None
            # Last move is back to the start.
            move = self.start
            edge = self.world.edges[self.node, move]
        else:
            edge = self.world.edges[self.node, move]
            self.visited.append(move)
            self.unvisited.remove(move)
        
        self.traveled.append(edge)
        self.distance += edge.length
        return edge