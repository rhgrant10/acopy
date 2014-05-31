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

        Parameters:
            world - the World in which the ant should seek solutions
            alpha - how much this ant considers pheromone
            beta - how much this ant considers distance
            start - coordinate from which this ant should find solutions

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
        A list of moves, where each move is a (start, end) coordinate tuple.
        """
        p, n = self.path, len(self.path)
        return [(p[i], p[(i + 1) % n]) for i in range(n)]
        
    def clone(self):
        """
        Return a new ant with exactly the same property values as this ant.

        Note that unlike copy, this method preserves even the UID of an Ant.

        """
        ant = Ant(self.world, self.alpha, self.beta, self.start)
        ant.uid = self.uid
        ant.node = self.node
        ant.path = self.path[:]
        ant.distance = self.distance
        ant.trip_complete = self.trip_complete
        return ant

    def __lt__(self, other):
        return self.distance < other.distance

    def reset(self, start=None):
        """
        Reset the ant so that it is ready to find another solution.

        Note that calling this method destroys the previous path, moves, and
        distance traveled by the ant.
        
        """
        self.start = start
        self.node = self.start
        self.distance = 0
        self.path = []
        self.trip_complete = False
        if start is not None:
            self.path.append(start)

    def can_move(self):
        """
        Return true if there is one or more coordinates not visited by the ant.
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
            if len(self.path) == len(self.world.nodes):
                # Close and complete the path.
                dist = self.world.edges[self.path[-1], self.path[0]].distance
                self.distance += dist
                self.trip_complete = True
            return move_made
        return None

    def get_possible_moves(self):
        """
        Return the set of all moves that can currently be made.
        """
        return set(self.world.nodes) - set(self.path)

    def choose_move(self, moves):
        """
        Return the one move to make from a list of moves.

        The default implementation uses weighted probability based on edge
        distance and pheromone level.

        """
        if len(moves) == 0:
            return None     # No more moves
        
        # Find the individual weight of each move.
        moves = list(moves) # it may be given as a set, but we need order
        weights = list()
        if self.node is None:
            weights = [1 for i in range(len(moves))]
        else:
            for m in moves:
                e = self.world.edges[self.node, m]
                pre = e.distance
                post = e.pheromone
                pre = 1 if pre == 0 else 1 / pre
                weights.append(self.calculate_weight(pre, post))
        
        # Normalize the weights without accedentally dividing by zero!
        total_weight = sum(weights)
        if total_weight == 0:
            total_weight = 1
        weights = [w / total_weight for w in weights]
        
        # Ensure the last element is 1 so that bisecting always returns a valid
        # index (instead of occasionally returning its length and producing an
        # error)
        cumdist = list(itertools.accumulate(weights)) + [1]
        
        # Choose a random place within the distrution of weights and return the
        # move at the index of would-be insertion.
        r = random.random()
        i = bisect.bisect(cumdist, r)
        return moves[i]
        
    def calculate_weight(self, pre, post):
        """
        Calculate the weight considering pre and post information.
        """
        return pow(post, self.alpha) * pow(pre, self.beta)

    def make_move(self, move):
        """
        Make the given move and update the distance traveled.
        """
        self.path.append(move)
        if len(self.path) == 1:
            self.start = move
        else:
            self.distance += self.world.edges[self.node, move].distance
        self.node = move
