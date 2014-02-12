from math import sqrt
from datetime import timedelta
import time
import random
import operator
import bisect
import json


"""
   .
..  
  .   .
"""
TEST_COORDS_5 = [
	(2,2),
	(3,1),
	(1,2),
	(4,3),
	(6,1)
]
TEST_COORDS_33 = [(34.02115,-84.267249),(34.021342,-84.363437),(34.022585,-84.36215),(34.022718,-84.361903),(34.023101,-84.36298),(34.024302,-84.16382),(34.044915,-84.255772),(34.045483,-84.221723),(34.046006,-84.225258),(34.048194,-84.262126),(34.048312,-84.208885),(34.048679,-84.224917),(34.04951,-84.226327),(34.051529,-84.218865),(34.055487,-84.217882),(34.056326,-84.20058),(34.059412,-84.216757),(34.060164,-84.242514),(34.060461,-84.237402),(34.061281,-84.334798),(34.061468,-84.33483),(34.061518,-84.243566),(34.062461,-84.240155),(34.063814,-84.225499),(34.064489,-84.22506),(34.066471,-84.217717),(34.068455,-84.283782),(34.068647,-84.283569),(34.071628,-84.265784),(34.10584,-84.21667),(34.109645,-84.177031),(34.116852,-84.163971),(34.118162,-84.163304)]


class World(object):
	"""
	A world consisting of one or more coordinates in which ants find the 
	shortest path that visits them all.

	"""
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
			self.distance = World.Edge.distance(a, b) if dist is None else dist
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

# class World
	def __init__(self, coords, p=.6, Q=1, t0=.1):
		"""
		Create a new world consisting of the given coordinates.

		The world is defined by a set of (x, y) coordinates, the assumption
		that each point can be reached from every other point, and a few 
		other variables.

		Parameters:
			coords - list of (x, y) coordinates
			p - percent of pheromone that evaporates after each iteration 
			    (default is 0.6)
			Q - amount of pheromone that each ant deposits after each iteration
			    (default is 1)
			t0 - inital amount of pheromone along each edge in the world
				(default is 0.1)

		"""
		self._set_rho(p)
		self._set_Q(Q)
		self._t0 = t0
		self._coords = coords
		self._edges = self._create_map()

	def _get_rho(self):
	    return self._rho
	def _set_rho(self, value):
	    self._p = value
	rho = property(
		fget=lambda self: self._get_rho,
		fset=lambda self, p: self._set_rho(p)
		)

	def _get_Q(self):
	    return self._Q
	def _set_Q(self, value):
	    self._q = value
	Q = property(
		fget=lambda self: self._get_rho,
		fset=lambda self, q: self._set_Q(q)
		)

	@property
	def coords(self):
	    return self._coords
	
	def _create_map(self):
		"""
		Create a map of the world from the coordinates.
		"""
		edges = {}
		for a in self._coords:
			for b in self._coords:
				edges[a, b] = World.Edge(a, b, pheromone=self._t0)
				edges[b, a] = World.Edge(b, a, 
					dist=edges[a, b].distance, pheromone=self._t0)
		return edges

	def get_distance(self, a, b):
		"""
		Return the distance of the edge between a and b.
		"""
		return self._edges[a, b].distance

	def get_scent(self, a, b):
		"""
		Return the amount of pheromone on the edge between a and b.
		"""
		return self._edges[a, b].pheromone

	def _reset(self):
		"""
		Reset the amount of pheromone on every edge to the initial default.
		"""
		for edge in self._edges.values():
			edge.pheromone = self._t0

	def solve(self, alpha=1, beta=2, iter_count=1000, ant_count=None):
		"""
		Find the shortest path that visits every coordinate.
		"""
		self._reset()
		
		# (Re-)Build the ant colony, placing Ants at coordinates in a round-robin
		# fashion.
		if ant_count is None or ant_count < 1:
			ant_count = len(self._coords)
		n = len(self._coords)
		ants = [Ant(self, alpha, beta, start=self._coords[i % n]) for i in xrange(ant_count)]
		
		# Yield local bests.
		# TODO: Add option to return global best.
		elite_ant = None
		for i in xrange(iter_count):
			self._find_solutions(ants)
			self._update_scent(ants)
			best_ant = self._get_best_ant(ants)
			if not elite_ant or best_ant < elite_ant:
				elite_ant = best_ant.clone()
			self._trace_elite(elite_ant)
			yield best_ant
			for ant in ants:
				ant.reset()

	def _trace_elite(self, ant, n=1):
		"""
		Deposit pheromone along the path of a particular ant n times.
		"""
		for m in ant.moves:
			self._edges[m].pheromone += n * self._q / ant.distance

	def _get_best_ant(self, ants):
		"""
		Return the ant with the shortest path.
		"""
		return sorted(ants)[0]

	def _find_solutions(self, ants):
		"""
		Let each ant find its way.
		"""
		ants_done = 0
		while ants_done < len(ants):
			ants_done = 0
			for ant in ants:
				if ant.can_move(): 	# TODO: Decide whether this 
					ant.move()		# 		is even necessary.
				else:
					ants_done += 1

	def _update_scent(self, ants):
		"""
		Update the amount of pheromone on each edge.
		"""
		for xy, edge in self._edges.iteritems():
			p, Q, t = self._p, self._q, edge.pheromone
			edge.pheromone = (1 - p) * t + sum(Q / a.distance for a in ants if xy in a.moves)
	

class Ant(object):
	"""
	A single independent finder of solutions to the world.
	
	"""
	uid = 0

	def __init__(self, world, a=1, b=2, start=None):
		"""
		Create a new Ant for the given world.

		Parameters:
			world - the World in which the ant should seek solutions
			a - how much this ant considers distance
			b - how much this ant considers scent
			start - coordinate from which this ant should find solutions

		"""
		self._uid = Ant.uid
		Ant.uid += 1
		self._world = world
		self.alpha = a
		self.beta = b
		self._trip_complete = False
		self.reset(start)

	def clone(self):
		"""
		Return a new ant with exactly the same property values as this ant.

		Note that unlike copy, this method preserves even the UID of an Ant.

		"""
		a = Ant(self._world, self._a, self._b, start=self._start)
		a._node = self._node
		a._path = self._path[:]
		a._traveled = self._traveled
		a._trip_complete = self._trip_complete
		return a

	def __lt__(self, other):
		return self.distance < other.distance
	
	@property
	def alpha(self):
	    return self._a
	@alpha.setter
	def alpha(self, value):
	    self._a = max(1, value)
		
	@property
	def beta(self):
	    return self._b
	@beta.setter
	def beta(self, value):
	    self._b = max(1, value)
			
	def attractiveness(self, move):
		"""
		Return a number suggesting how attractive a particular move seems.

		The default implementation uses inverse distance, but any apriori
		knowledge can be used instead.

		"""
		if self._node is None:
			return 1
		return 1 / float(self._world.get_distance(self._node, move))
		
	def trail_level(self, move):
		"""
		Return a number suggesting the amount of pheromone on the way to a move.
		"""
		if self._node is None:
			return float(1)
		return self._world.get_scent(self._node, move)

	def log(self, msg):
		"""
		Prints a message with the current timestamp and the ant's UID.
		"""
		print "%s [Ant #%s] %s" % (time.time(), self._uid, msg)

	def reset(self, start=None):
		"""
		Reset the ant so that it is ready to find another solution.

		Note that calling this method destroys the previous path, moves, and 
		distance traveled by the ant.

		"""
		self._node = start
		self._traveled = 0
		self._path = []
		self._trip_complete = False
		if start is not None:
			self._path.append(start)

	def can_move(self):
		"""
		Return true if there is one or more coordinates not visited by the ant.
		"""
		return not self._trip_complete

	def move(self):
		"""
		Choose a valid move and make it.
		"""
		moves = self.get_possible_moves()
		move = self.choose_move(moves)
		if move:
			self.make_move(move)
			if len(self._path) == len(self._world.coords):
				self._traveled += self._world.get_distance(self._path[-1], self._path[0])
				self._trip_complete = True

	def get_possible_moves(self):
		"""
		Return the set of all moves that can currently be made.
		"""
		return set(self._world.coords) - set(self._path)

	def choose_move(self, moves):
		"""
		Return the one move to make from a list of moves.

		The default implementation uses weighted probability based on edge 
		distance and pheromone level.

		"""
		if len(moves) == 0:
			return None	# No more moves
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
		n = self.attractiveness(move)
		t = self.trail_level(move)
		w = pow(n, self._a) * pow(t, self._b)
		return w

	def make_move(self, move):
		"""
		Make the given move and update the distance traveled.
		"""
		self._path.append(move)
		if len(self._path) == 1:
			self._start = move
		else:
			self._traveled += self._world.get_distance(self._node, move)
		self._node = move
		
	@property
	def path(self):
		return tuple(self._path)
	
	@property
	def distance(self):
	    return self._traveled

	@property
	def moves(self):
		if len(self._path) == 0:
			return []
		path = self._path[:]
		starts = path[::2]
		path.append(path.pop(0))
		ends = path[::2]
		return zip(starts, ends)


if __name__ == '__main__':
	world = World(TEST_COORDS_33, p=.6, Q=1)
	fastest = None
	niters = 100
	print "\n{:21}{:12}{:20}".format("Time Elapsed", "Trial", "Distance")
	print "-" * (25 + 12 + 20)
	start_time = time.time()
	for i, ant in enumerate(world.solve()):
		if fastest is None:
			fastest = ant
		if ant.distance < fastest.distance:
			fastest = ant
			fastest_time = time.time() - start_time
			print "{:>20} {:<12}{:<20}".format(
				timedelta(seconds=fastest_time), i, fastest.distance)
	total_time = time.time() - start_time
	print "\nTotal time for {} iterations: {}".format(niters, timedelta(seconds=total_time))
	print "-" * (25 + 12 + 20)
	print "Best solution:"
	i = 0
	for x, y in fastest.path:
		print "  {:>8} = ({:0.6f}, {:0.6f})".format(world.coords.index((x,y)), x, y)
		i += 1
	print "Time for best solution: {}".format(timedelta(seconds=fastest_time))
	
