from math import sqrt
from datetime import timedelta
import itertools
import time
import random
import operator
import bisect

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

class Edge:
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
        
        
class Solver:
    """
    A world consisting of one or more coordinates in which ants find the
    shortest path that visits them all.

    """
    def __init__(self, world, **kwargs):
        self.world = world
        self.rho = kwargs.get('rho', 0.75)
        self.q = kwargs.get('Q', 1)
        self.t0 = kwargs.get('t0', .01)
        self.alpha = kwargs.get('alpha', 1.2)
        self.beta = kwargs.get('beta', 3)
        self.ant_count = kwargs.get('ant_count', 10)
        self.elite = kwargs.get('elite', .5)
        
    def solve(self, iter_count=20000):
        """
        Find the shortest path that visits every coordinate.
        """
        # Reset the amount of pheromone on every edge to the initial default.
        for edge in self.world.edges.values():
            edge.pheromone = self.t0

        # Yield local bests.
        # TODO: Add option to return global best.
        elite_ant = None
        for i in range(iter_count):
            # (Re-)Build the ant colony
            ants = self.round_robin_ants() if self.ant_count < 1 \
                    else self.random_ants()
            
            self.find_solutions(ants)
            self.update_scent(ants)
            best_ant = self.get_best_ant(ants)
            if elite_ant is None or best_ant < elite_ant:
                elite_ant = best_ant.clone()
            if self.elite:
                self.trace_elite(elite_ant)
            yield best_ant
    
    def round_robin_ants(self):
        n = len(self.world.coords)
        return [Ant(self.world, self.alpha, self.beta, start=self.world.coords[i % n])
            for i in range(self.ant_count)
        ]
        
    def random_ants(self):
        starts = self.world.coords[:]
        ants = list()
        while self.ant_count > 0 and len(starts) > 0:
            r = random.randrange(len(starts))
            ants.append(Ant(self.world, self.alpha, self.beta, start=starts.pop(r)))
        return ants

    def find_solutions(self, ants):
        """
        Let each ant find its way.
        """
        ants_done = 0
        while ants_done < len(ants):
            ants_done = 0
            for ant in ants:
                if ant.can_move():
                    m = ant.move()
                    self.world.edges[m].pheromone *= self.rho
                else:
                    ants_done += 1

    def update_scent(self, ants):
        """
        Update the amount of pheromone on each edge.
        """
        ants = sorted(ants)[:len(ants) // 2]
        for move, edge in self.world.edges.items():
            edge.pheromone = (1 - self.rho) * edge.pheromone + \
                    sum(self.q / a.distance for a in ants if move in a.moves)
            if edge.pheromone < self.t0:
                edge.pheromone = self.t0

    def get_best_ant(self, ants):
        """
        Return the ant with the shortest path.
        """
        return sorted(ants)[0]

    def trace_elite(self, ant):
        """
        Deposit pheromone along the path of a particular ant n times.
        """
        if self.elite:
            for m in ant.moves:
                self.world.edges[m].pheromone += self.elite * self.q / ant.distance
    

class World:
    def __init__(self, coords, edges=None):
        """
        Create a new world consisting of the given coordinates.

        The world is defined by a set of (x, y) coordinates, the assumption
        that each point can be reached from every other point, and a few
        other variables.

        Parameters:
            coords - list of (x, y) coordinates
            edges - dict of Edge instances with node-pair tuples as keys

        """
        self.coords = coords
        self.edges = edges or self.create_map()
        
    def create_map(self):
        """
        Create a map of the world from the coordinates.
        """
        edges = {}
        for a in self.coords:
            for b in self.coords:
                edges[a, b] = Edge(a, b)
                edges[b, a] = Edge(b, a, dist=edges[a, b].distance)
        return edges

    def distance(self, a, b):
        """
        Return the distance of the edge between a and b.
        """
        e = self.edges.get((a, b), None)
        return e.distance if e is not None else 0

    def scent(self, a, b):
        """
        Return the amount of pheromone on the edge between a and b.
        """
        e = self.edges.get((a, b), None)
        return e.pheromone if e is not None else 0


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

    
if __name__ == '__main__':
    world = World(TEST_COORDS_33)
    solver = Solver(world)
    print("""rho={w.rho}, Q={w.q}
alpha={w.alpha}, beta={w.beta}
elite={w.elite}""".format(w=solver))
    
    divider = "-" * (25 + 12 + 20)
    header = "\n{:21}{:12}{:20}".format("Time Elapsed", "Trial", "Distance")
    
    print(header)
    print(divider)
    fastest = None
    start_time = time.time()
    for i, ant in enumerate(solver.solve()):
        if fastest is None or ant.distance < fastest.distance:
            fastest = ant.clone()
            fastest_time = time.time() - start_time
            print("{:>20} {:<12}{:<20}".format(
                    timedelta(seconds=fastest_time), i, fastest.distance))
    total_time = time.time() - start_time
    
    print("\nTotal time for {} iterations: {}".format(
            i + 1,
            timedelta(seconds=total_time)))

    print(divider)
    print("Best solution:")
    for x, y in fastest.path:
        print("  {:>8} = ({:0.6f}, {:0.6f})".format(
                world.coords.index((x, y)),
                x,
                y))
    print("Time for best solution: {}".format(timedelta(seconds=fastest_time)))
