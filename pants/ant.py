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
        if len(self.path) == 0:
            return []
        path = self.path[:]
        starts = path[::2]
        path.append(path.pop(0))
        ends = path[::2]
        return zip(starts, ends)

    def clone(self):
        """
        Return a new ant with exactly the same property values as this ant.

        Note that unlike copy, this method preserves even the UID of an Ant.

        """
        ant = Ant(self.world, self.alpha, self.beta, self.start)
        ant.node = self.node
        ant.path = self.path[:]
        ant.distance = self.distance
        ant.trip_complete = self.trip_complete
        return ant

    def __lt__(self, other):
        return self.distance < other.distance

    def get_apriori(self, move):
        """
        Return a number suggesting how attractive a particular move seems.

        The default implementation uses inverse distance, but any apriori
        knowledge can be used instead.

        """
        if self.node is None:
            return 1
        return 1 / float(self.world.distance(self.node, move))

    def get_posteriori(self, move):
        """
        Return a number suggesting the amount of pheromone on the way to a move.
        """
        if self.node is None:
            return float(1)
        return self.world.scent(self.node, move)

    def log(self, msg):
        """
        Prints a message with the current timestamp and the ant's UID.
        """
        print("%s [Ant #%s] %s" % (time.time(), self.uid, msg))

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
        return not self.trip_complete

    def move(self):
        """
        Choose a valid move and make it.
        """
        moves = self.get_possible_moves()
        move = self.choose_move(moves)
        if move:
            move_made = (self.node, move)
            self.make_move(move)
            if len(self.path) == len(self.world.coords):
                # Close and complete the path.
                self.distance += self.world.distance(
                    self.path[-1], self.path[0]
                )
                self.trip_complete = True
            return move_made
        return None

    def get_possible_moves(self):
        """
        Return the set of all moves that can currently be made.
        """
        return set(self.world.coords) - set(self.path)

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
        weights = [self.calculate_weight(m) for m in moves]
        
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
        
    def calculate_weight(self, move):
        """
        Return a number representing the weight of a single move.
        """
        p = self.get_posteriori(move)   # pheromone
        d = self.get_apriori(move)      # distance
        return pow(p, self.alpha) * pow(d, self.beta)

    def make_move(self, move):
        """
        Make the given move and update the distance traveled.
        """
        self.path.append(move)
        if len(self.path) == 1:
            self.start = move
        else:
            self.distance += self.world.distance(self.node, move)
        self.node = move

