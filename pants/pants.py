from copy import copy, deepcopy
from math import sqrt
from datetime import timedelta
import time
import random
import operator
import bisect
import json

# TODO: Clean this up and put it somewhere else!
TEST_COORDS_5 = [
    (2, 2),
    (3, 1),
    (1, 2),
    (4, 3),
    (6, 1)
]

# TODO: Clean this up and put it somewhere else!
TEST_COORDS_33 = [
    (34.021150, -84.267249), (34.021342, -84.363437), (34.022585, -84.362150),
    (34.022718, -84.361903), (34.023101, -84.362980), (34.024302, -84.163820),
    (34.044915, -84.255772), (34.045483, -84.221723), (34.046006, -84.225258),
    (34.048194, -84.262126), (34.048312, -84.208885), (34.048679, -84.224917),
    (34.049510, -84.226327), (34.051529, -84.218865), (34.055487, -84.217882),
    (34.056326, -84.200580), (34.059412, -84.216757), (34.060164, -84.242514),
    (34.060461, -84.237402), (34.061281, -84.334798), (34.063814, -84.225499),
    (34.061468, -84.334830), (34.061518, -84.243566), (34.062461, -84.240155),
    (34.064489, -84.225060), (34.066471, -84.217717), (34.068455, -84.283782),
    (34.068647, -84.283569), (34.071628, -84.265784), (34.105840, -84.216670),
    (34.109645, -84.177031), (34.116852, -84.163971), (34.118162, -84.163304)
]

class Edge(object):
    """
    The connection between to coordinates.

    Each edge is composed of a distance and an amount of pheromone.

    """
    def __init__(self, a, b, dist=None, pheromone=0.1):
        """
        Create a new Edge between a and b.

        Parameters:
            a - the start of the edge
            b - the end of the edge
            dist - the distance between a and b (defaults to Euclidean)
            pheromone - the initial amount of pheromone (defaults to 0.1)

        """
        self.start = a
        self.end = b
        self.distance = Edge.distance(a, b) if dist is None else dist
        self.pheromone = 0.1 if pheromone is None else pheromone

    @staticmethod
    def distance(a, b):
        """
        Return the Euclidean distance between a and b.

        Parameters:
            a - the first point (x1, y1)
            b - the second point (x2, y2)
        Returns:
            sqrt((x2 - x1)^2 + (y2 - y1)^2)

        """
        x = b[0] - a[0]
        y = b[1] - a[1]
        return sqrt(x*x + y*y)
        
        
class World(object):
    """
    A world consisting of one or more coordinates in which ants find the
    shortest path that visits them all.

    """
    def __init__(self, coords, rho=.6, Q=1, t0=1):
        """
        Create a new world consisting of the given coordinates.

        The world is defined by a set of (x, y) coordinates, the assumption
        that each point can be reached from every other point, and a few
        other variables.

        Parameters:
            coords - list of (x, y) coordinates
            rho - percent of pheromone that evaporates after each iteration
                (default is 0.6)
            Q - amount of pheromone that each ant deposits after each iteration
                (default is 1)
            t0 - inital amount of pheromone along each edge in the world
                (default is 0.1)

        """
        self.rho = rho
        self.q = Q
        self.t0 = t0
        self.coords = coords
        self.edges = self.create_map()

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        for k, v in self.__dict__.iteritems():
            setattr(new, k, deepcopy(v, memo))
        return new

    def create_map(self):
        """
        Create a map of the world from the coordinates.
        """
        edges = {}
        for a in self.coords:
            for b in self.coords:
                edges[a, b] = Edge(a, b, pheromone=self.t0)
                edges[b, a] = Edge(b, a,
                        dist=edges[a, b].distance, pheromone=self.t0
                )
        return edges

    def get_distance(self, a, b):
        """
        Return the distance of the edge between a and b.
        """
        return self.edges[a, b].distance

    def get_scent(self, a, b):
        """
        Return the amount of pheromone on the edge between a and b.
        """
        return self.edges[a, b].pheromone

    def reset(self):
        """
        Reset the amount of pheromone on every edge to the initial default.
        """
        for edge in self.edges.values():
            edge.pheromone = self.t0

    def solve(self, alpha=.1, beta=1, iter_count=1000, ant_count=None):
        """
        Find the shortest path that visits every coordinate.
        """
        self.reset()

        # (Re-)Build the ant colony, placing Ants at coordinates in a round-
        # robin fashion.
        if ant_count is None or ant_count < 1:
            ant_count = len(self.coords)
        n = len(self.coords)
        ants = [Ant(self, alpha, beta, start=self.coords[i % n]) 
            for i in xrange(ant_count)
        ]

        # Yield local bests.
        # TODO: Add option to return global best.
        elite_ant = None
        for i in xrange(iter_count):
            self.find_solutions(ants)
            self.update_scent(ants)
            best_ant = self.get_best_ant(ants)
            if elite_ant is None or best_ant < elite_ant:
                elite_ant = best_ant.clone()
            self.trace_elite(elite_ant)
            yield best_ant
            for ant in ants:
                ant.reset()

    def trace_elite(self, ant, n=1):
        """
        Deposit pheromone along the path of a particular ant n times.
        """
        for m in ant.moves:
            self.edges[m].pheromone += n * self.q / ant.distance

    def get_best_ant(self, ants):
        """
        Return the ant with the shortest path.
        """
        return sorted(ants)[0]

    def find_solutions(self, ants):
        """
        Let each ant find its way.
        """
        ants_done = 0
        while ants_done < len(ants):
            ants_done = 0
            for ant in ants:
                if ant.can_move():  # TODO: Decide whether this
                    ant.move()      #       is even necessary.
                else:
                    ants_done += 1

    def update_scent(self, ants):
        """
        Update the amount of pheromone on each edge.
        """
        for xy, edge in self.edges.iteritems():
            rho, Q, t = self.rho, self.q, edge.pheromone
            edge.pheromone = (1 - rho) * t + sum(
                Q / a.distance for a in ants if xy in a.moves
            )


class Ant(object):
    """
    A single independent finder of solutions to the world.

    """
    uid = 0

    def __init__(self, world, alpha=2, beta=3, start=None):
        """
        Create a new Ant for the given world.

        Parameters:
            world - the World in which the ant should seek solutions
            alpha - how much this ant considers distance
            beta - how much this ant considers scent
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
    def alpha(self):
        """
        The level of attention paid to distance.
        """
        return self._alpha
    @alpha.setter
    def alpha(self, value):
        """
        Set the level of attention paid to the distance.
        """
        self._alpha = max(1, value)
        
    @property
    def beta(self):
        """
        The level of attention paid to pheromone.
        """
        return self._beta
    @beta.setter
    def beta(self, value):
        """
        Set the level of attention paid to the pheromone.
        """
        self._beta = max(1, value)

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

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        for k, v in self.__dict__.iteritems():
            setattr(new, k, deepcopy(v, memo))
        return new

    def clone(self):
        """
        Return a new ant with exactly the same property values as this ant.

        Note that unlike copy, this method preserves even the UID of an Ant.

        """
        a = Ant(self.world, self.alpha, self.beta, self.start)
        a.node = self.node
        a.path = self.path[:]
        a.distance = self.distance
        a.trip_complete = self.trip_complete
        return a

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
        return 1 / float(self.world.get_distance(self.node, move))

    def get_posteriori(self, move):
        """
        Return a number suggesting the amount of pheromone on the way to a move.
        """
        if self.node is None:
            return float(1)
        return self.world.get_scent(self.node, move)

    def log(self, msg):
        """
        Prints a message with the current timestamp and the ant's UID.
        """
        print "%s [Ant #%s] %s" % (time.time(), self.uid, msg)

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
            self.make_move(move)
            if len(self.path) == len(self.world.coords):
                self.distance += self.world.get_distance(
                    self.path[-1], self.path[0]
                )
                self.trip_complete = True

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
        weighted_moves = []
        for m in moves:
            w = (m, self.calculate_weight(m))
            weighted_moves.append(w)
        moves, weights = zip(*weighted_moves)
        cumdist = list(self._accumulate(weights))
        r = random.random() * cumdist[-1]
        i = bisect.bisect(cumdist, r)
        try:
            return moves[i]
        except IndexError as ie:
            return moves[-1]

    def _accumulate(self, iterable, func=operator.add):
        """
        Stand-in replacement for the missing itertools.accumulate.
        """
        it = iter(iterable)
        total = next(it)
        yield total
        for element in it:
            total = func(total, element)
            yield total

    def calculate_weight(self, move):
        """
        Return a number representing the weight of a single move.
        """
        n = self.get_apriori(move)
        t = self.get_posteriori(move)
        w = pow(n, self.alpha) * pow(t, self.beta)
        return w

    def make_move(self, move):
        """
        Make the given move and update the distance traveled.
        """
        self.path.append(move)
        if len(self.path) == 1:
            self.start = move
        else:
            self.distance += self.world.get_distance(self.node, move)
        self.node = move

    
if __name__ == '__main__':
    world = World(TEST_COORDS_33)
    fastest = None
    
    print "\n{:21}{:12}{:20}".format("Time Elapsed", "Trial", "Distance")
    print "-" * (25 + 12 + 20)
    start_time = time.time()
    for i, ant in enumerate(world.solve(iter_count=100)):
        if fastest is None or ant.distance < fastest.distance:
            fastest = ant.clone()
            fastest_time = time.time() - start_time
        print "{:>20} {:<12}{:<20}".format(
            timedelta(seconds=fastest_time), i, fastest.distance
        )

    total_time = time.time() - start_time
    print "\nTotal time for {} iterations: {}".format(
        i + 1,
        timedelta(seconds=total_time)
    )

    print "-" * (25 + 12 + 20)
    print "Best solution:"
    i = 0
    for x, y in fastest.path:
        print "  {:>8} = ({:0.6f}, {:0.6f})".format(
            world.coords.index((x, y)), x, y
        )
        i += 1
    print "Time for best solution: {}".format(timedelta(seconds=fastest_time))
