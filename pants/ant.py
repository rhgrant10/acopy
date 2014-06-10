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

class Ant:
    """
    A single independent finder of solutions to the world.

    """
    uid = 0

    def __init__(self, world, alpha=1, beta=3, start=None):
        """
        Create a new Ant for the given world.

        :param World world: the world in which to travel
        :param float alpha: the relative importance of pheromone (default=1)
        :param float beta: the relative importance of distance (default=3)
        :param Node start: the starting node (default=None)

        """
        Ant.uid = self.uid = Ant.uid + 1
        self.world = world
        self.alpha = alpha
        self.beta = beta
        self.trip_complete = False
        self.distance = 0
        self.reset(start)

    @property
    def moves(self):
        """
        Return a list of the moves made so far
        
        :returns: A list of (start, end) tuples
        :rtype: list
        
        """
        # TODO: Decide whether to simply return edges.
        p, n = self.path, len(self.path)
        return [(p[i], p[(i + 1) % n]) for i in range(n)]
        
    def clone(self):
        """
        Return a new :class:`Ant` with exactly the same property values.

        Note that unlike copy, this method preserves even the UID of an Ant.

        :returns: a clone
        :rtype: :class:`Ant`

        """
        ant = Ant(self.world, self.alpha, self.beta, self.start)
        ant.uid = self.uid
        ant.node = self.node
        ant.path = self.path[:]
        ant.distance = self.distance
        return ant

    def __lt__(self, other):
        return self.distance < other.distance

    def reset(self, start=None):
        """
        Reset everything so that a new solution can be found.

        Note that calling this method destroys the previous path, moves, and
        distance traveled by the ant.
        
        :param Node start: which :class:`Node` to start the next solution from
                           (by default, the previous starting :class:`Node` is
                            used again)
        
        """
        self.start = start
        self.node = self.start
        self.distance = 0
        self.path = []
        if start is not None:
            self.path.append(start)

    def can_move(self):
        """
        Return true if there are more than zero possible moves to make.

        """
        return len(self.path) < len(self.world.nodes)

    def move(self):
        """
        Choose a valid move and make it.

        """
        moves = self.get_possible_moves()
        move = self.choose_move(moves)
        if move:
            move_made = (self.node, move)
            self.make_move(move)
            return move_made
        return None

    def get_possible_moves(self):
        """
        Return the set of all moves that can currently be made.

        :returns: all currently possible moves
        :rtype: set
        
        """
        return set(self.world.nodes) - set(self.path)

    def choose_move(self, moves):
        """
        Return which move to make by choosing from *moves*.
        
        :param list moves: a list of all possible moves
        
        :returns: the move to make
        :rtype: :class:`Node`
        
        """
        N = len(moves)
        if N == 0:
            return None     # No more moves
        
        # Find the individual weight of each move.
        moves = list(moves) # it may be given as a set, but we need order
        weights = []
        if self.node is None:
            weights = [1 for i in range(N)]
        else:
            for m in moves:
                e = self.world.edges[self.node, m]
                weights.append(self.calculate_weight(e))
        
        # Ensure the index of the last element is never exceeded.
        total_weight = sum(weights) or 1
        cumdist = list(itertools.accumulate(weights)) + [total_weight]
        
        # Choose a random place within the distrution of weights and return the
        # move at the index of would-be insertion.
        r = random.random() * total_weight
        i = bisect.bisect(cumdist, r)
        return moves[i]
        
    def calculate_weight(self, e):
        """
        Calculate the weight of the given :class:`Edge` *e*.
        
        :param Edge e: the edge of which the weight shall be calculated

        :returns: the weight (projected usefullness) of *e*
        :rtype: float
        
        """
        return e.pheromone ** self.alpha * (1 / (e.length or 1)) ** self.beta

    def make_move(self, move):
        """
        Perform the given *move*.
        
        :param Node move: the :class:`Node` to move to
        
        """
        self.path.append(move)
        n = len(self.path)
        
        # If moving to the starting node, no distance was actually traveled.
        if n == 1:
            self.start = move        
        else:
            self.distance += self.world.edges[self.node, move].length
        
        # If moving to the last node, add the distance from the last node back
        # to the first node to "complete" the path.
        if n == len(self.world.nodes):
            final = self.world.edges[self.path[-1], self.path[0]].length
            self.distance += final

        self.node = move
