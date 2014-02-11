from math import sqrt
from datetime import timedelta
import time
import random
import operator
import bisect
import json


TEST_COORDS = [(34.02115,-84.267249),(34.021342,-84.363437),(34.022585,-84.36215),(34.022718,-84.361903),(34.023101,-84.36298),(34.024302,-84.16382),(34.044915,-84.255772),(34.045483,-84.221723),(34.046006,-84.225258),(34.048194,-84.262126),(34.048312,-84.208885),(34.048679,-84.224917),(34.04951,-84.226327),(34.051529,-84.218865),(34.055487,-84.217882),(34.056326,-84.20058),(34.059412,-84.216757),(34.060164,-84.242514),(34.060461,-84.237402),(34.061281,-84.334798),(34.061468,-84.33483),(34.061518,-84.243566),(34.062461,-84.240155),(34.063814,-84.225499),(34.064489,-84.22506),(34.066471,-84.217717),(34.068455,-84.283782),(34.068647,-84.283569),(34.071628,-84.265784),(34.10584,-84.21667),(34.109645,-84.177031),(34.116852,-84.163971),(34.118162,-84.163304)]
TEST_225 = [
	(155.42, 150.65),
	(375.92, 164.65),
	(183.92, 150.65),
	(205.42, 150.65),
	(205.42, 171.65),
	(226.42, 171.65),
	(226.42, 186.15),
	(226.42, 207.15),
	(226.42, 235.65),
	(226.42, 264.15),
	(226.42, 292.65),
	(226.42, 314.15),
	(226.42, 335.65),
	(205.42, 335.65),
	(190.92, 335.65),
	(190.92, 328.15),
	(176.92, 328.15),
	(176.92, 299.65),
	(155.42, 299.65),
	(155.42, 328.15),
	(155.42, 356.65),
	(183.92, 356.65),
	(219.42, 356.65),
	(240.92, 356.65),
	(269.42, 356.65),
	(290.42, 356.65),
	(387.42, 136.15),
	(318.92, 356.65),
	(318.92, 335.65),
	(318.92, 328.15),
	(318.92, 299.65),
	(297.92, 299.65),
	(290.42, 328.15),
	(290.42, 335.65),
	(297.92, 328.15),
	(254.92, 335.65),
	(254.92, 314.15),
	(254.92, 292.65),
	(254.92, 271.65),
	(254.92, 243.15),
	(254.92, 221.65),
	(254.92, 193.15),
	(254.92, 171.65),
	(276.42, 171.65),
	(296.42, 150.65),
	(276.42, 150.65),
	(375.92, 150.65),
	(308.92, 150.65),
	(354.92, 164.65),
	(338.42, 174.65),
	(354.92, 174.65),
	(338.42, 200.15),
	(338.42, 221.65),
	(354.92, 221.65),
	(354.92, 200.15),
	(361.92, 200.15),
	(361.92, 186.15),
	(383.42, 186.15),
	(383.42, 179.15),
	(404.42, 179.15),
	(404.42, 186.15),
	(418.92, 186.15),
	(418.92, 200.15),
	(432.92, 200.15),
	(432.92, 221.65),
	(418.92, 221.65),
	(418.92, 235.65),
	(397.42, 235.65),
	(397.42, 243.15),
	(375.92, 243.15),
	(375.92, 257.15),
	(368.92, 257.15),
	(368.92, 264.15),
	(347.42, 264.15),
	(347.42, 278.65),
	(336.42, 278.65),
	(336.42, 328.15),
	(347.42, 328.15),
	(347.42, 342.65),
	(368.92, 342.65),
	(368.92, 353.65),
	(418.92, 353.65),
	(418.92, 342.65),
	(432.92, 342.65),
	(432.92, 356.65),
	(447.42, 356.65),
	(447.42, 321.15),
	(447.42, 292.65),
	(432.92, 292.65),
	(432.92, 314.15),
	(418.92, 314.15),
	(418.92, 321.15),
	(397.42, 321.15),
	(397.42, 333.65),
	(375.92, 333.65),
	(375.92, 321.15),
	(361.92, 321.15),
	(361.92, 299.65),
	(375.92, 299.65),
	(375.92, 285.65),
	(397.42, 285.65),
	(397.42, 271.65),
	(418.92, 271.65),
	(418.92, 264.15),
	(439.92, 264.15),
	(439.92, 250.15),
	(454.42, 250.15),
	(454.42, 243.15),
	(461.42, 243.15),
	(461.42, 214.65),
	(461.42, 193.15),
	(447.42, 193.15),
	(447.42, 179.15),
	(439.92, 179.15),
	(439.92, 167.65),
	(419.92, 167.65),
	(419.92, 150.65),
	(439.92, 150.65),
	(454.42, 150.65),
	(475.92, 150.65),
	(475.92, 171.65),
	(496.92, 171.65),
	(496.92, 193.15),
	(496.92, 214.65),
	(496.92, 243.15),
	(496.92, 271.65),
	(496.92, 292.65),
	(496.92, 317.15),
	(496.92, 335.65),
	(470.42, 335.65),
	(470.42, 356.65),
	(496.92, 356.65),
	(347.42, 150.65),
	(539.92, 356.65),
	(560.92, 356.65),
	(589.42, 356.65),
	(589.42, 342.65),
	(603.92, 342.65),
	(610.92, 342.65),
	(610.92, 335.65),
	(610.92, 321.15),
	(624.92, 321.15),
	(624.92, 278.65),
	(610.92, 278.65),
	(610.92, 257.15),
	(589.42, 257.15),
	(589.42, 250.15),
	(575.42, 250.15),
	(560.92, 250.15),
	(542.92, 250.15),
	(542.92, 264.15),
	(560.92, 264.15),
	(575.42, 264.15),
	(575.42, 271.65),
	(582.42, 271.65),
	(582.42, 285.65),
	(596.42, 285.65),
	(560.92, 335.65),
	(596.42, 314.15),
	(582.42, 314.15),
	(582.42, 321.15),
	(575.42, 321.15),
	(575.42, 335.65),
	(525.42, 335.65),
	(525.42, 314.15),
	(525.42, 299.65),
	(525.42, 281.65),
	(525.42, 233.15),
	(525.42, 214.65),
	(525.42, 193.15),
	(525.42, 171.65),
	(546.92, 171.65),
	(546.92, 150.65),
	(568.42, 150.65),
	(475.92, 160.65),
	(603.92, 150.65),
	(624.92, 150.65),
	(624.92, 136.15),
	(596.42, 136.15),
	(575.42, 136.15),
	(553.92, 136.15),
	(532.42, 136.15),
	(575.42, 356.65),
	(489.92, 136.15),
	(468.42, 136.15),
	(447.42, 136.15),
	(425.92, 136.15),
	(404.42, 136.15),
	(370.42, 136.15),
	(361.92, 150.65),
	(340.42, 136.15),
	(326.42, 136.15),
	(301.92, 136.15),
	(276.42, 136.15),
	(254.92, 136.15),
	(315.92, 136.15),
	(212.42, 136.15),
	(190.92, 136.15),
	(338.92, 150.65),
	(155.42, 136.15),
	(624.92, 299.65),
	(318.92, 321.65),
	(155.42, 314.15),
	(311.92, 356.65),
	(355.42, 136.15),
	(318.92, 314.15),
	(362.92, 164.65),
	(254.92, 356.65),
	(383.42, 333.65),
	(447.42, 335.65),
	(470.42, 345.65),
	(525.42, 250.15),
	(546.92, 335.65),
	(525.42, 261.15),
	(525.42, 356.65),
	(336.42, 298.65),
	(336.42, 313.15),
	(293.42, 136.15),
	(336.42, 306.15),
	(425.92, 264.15),
	(391.42, 353.65),
	(482.92, 335.65),
	(429.92, 167.65),
	(330.92, 150.65),
	(368.42, 150.65)
]

TEST_225_TOUR = [
	1,
	200,
	198,
	197,
	195,
	194,
	218,
	193,
	196,
	192,
	191,
	205,
	189,
	27,
	188,
	187,
	186,
	185,
	184,
	182,
	181,
	180,
	179,
	178,
	177,
	176,
	174,
	173,
	172,
	171,
	170,
	169,
	168,
	212,
	214,
	167,
	166,
	165,
	164,
	213,
	158,
	163,
	162,
	161,
	160,
	159,
	157,
	156,
	155,
	154,
	153,
	152,
	151,
	150,
	149,
	148,
	147,
	146,
	145,
	144,
	143,
	201,
	142,
	141,
	140,
	139,
	138,
	137,
	136,
	183,
	135,
	134,
	215,
	132,
	131,
	211,
	130,
	222,
	129,
	128,
	127,
	126,
	125,
	124,
	123,
	122,
	121,
	175,
	120,
	119,
	118,
	117,
	116,
	223,
	115,
	114,
	113,
	112,
	111,
	110,
	109,
	108,
	107,
	106,
	105,
	220,
	104,
	103,
	102,
	101,
	100,
	99,
	98,
	97,
	96,
	95,
	209,
	94,
	93,
	92,
	91,
	90,
	89,
	88,
	87,
	210,
	86,
	85,
	84,
	83,
	82,
	221,
	81,
	80,
	79,
	78,
	77,
	217,
	219,
	216,
	76,
	75,
	74,
	73,
	72,
	71,
	70,
	69,
	68,
	67,
	66,
	65,
	64,
	63,
	62,
	61,
	60,
	59,
	58,
	57,
	56,
	55,
	54,
	53,
	52,
	50,
	51,
	49,
	207,
	2,
	47,
	225,
	190,
	133,
	199,
	224,
	48,
	45,
	46,
	44,
	43,
	42,
	41,
	40,
	39,
	38,
	37,
	36,
	34,
	33,
	35,
	32,
	31,
	206,
	202,
	30,
	29,
	28,
	204,
	26,
	25,
	208,
	24,
	23,
	22,
	21,
	20,
	203,
	19,
	18,
	17,
	16,
	15,
	14,
	13,
	12,
	11,
	10,
	9,
	8,
	7,
	6,
	5,
	4,
	3
]


class World(object):
	class Edge(object):
		def __init__(self, a, b, dist=None, phermone=0.1):
			self.start = a
			self.end = b
			self.distance = World.Edge.distance(a, b) if dist is None else dist
			self.phermone = 0.1 if phermone is None else phermone

		@staticmethod
		def distance(a, b):
			x = b[0] - a[0]
			y = b[1] - a[1]
			return sqrt(x*x + y*y)

# class World
	def __init__(self, coords, p=.5, Q=10, t0=.1):
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
		edges = {}
		for a in self._coords:
			for b in self._coords:
				edges[a, b] = World.Edge(a, b, phermone=self._t0)
				edges[b, a] = World.Edge(b, a, 
					dist=edges[a, b].distance, phermone=self._t0)
		return edges

	def get_distance(self, a, b):
		return self._edges[a, b].distance

	def get_scent(self, a, b):
		return self._edges[a, b].phermone

	def _reset(self):
		for edge in self._edges.values():
			edge.phermone = self._t0

	def solve(self, alpha=1, beta=2, iter_count=None, ant_count=None):
		self._reset()
		if ant_count is None or ant_count < 1:
			ant_count = len(self._coords)

		ants = []
		i = 0
		n = len(self._coords)
		while len(ants) < ant_count:
			ants.append(Ant(self, alpha, beta, start=self._coords[i % n]))
			i += 1

		if iter_count is None:
			iter_count = 1000

		# We iterate iter_count times.
		elite_ant = None
		for i in xrange(iter_count):
			self._find_solutions(ants)
			self._update_scent(ants)
			best_ant = self._get_best_ant(ants)
			if not elite_ant or best_ant < elite_ant:
				elite_ant = best_ant.clone()
			self._trace_elite(elite_ant)
			yield elite_ant
			for ant in ants:
				ant.reset()

	def _trace_elite(self, ant, n=1):
		for m in ant.moves:
			self._edges[m].phermone += n * self._q / ant.distance

	def _sort_paths(self, ants):
		return tuple(sorted(
			[(ant.distance, tuple(ant.path)) for ant in ants],
			key=lambda x: x[0]
			))

	def _get_best_ant(self, ants):
		return sorted(ants, key=lambda ant: ant.distance)[0]

	def _agreement(self, ants):
		return False	# TODO: Implement path comparison.

	def _find_solutions(self, ants):
		ants_done = 0
		while ants_done < len(ants):
			ants_done = 0
			for ant in ants:
				if ant.can_move():
					ant.move()
				else:
					ants_done += 1

	def _update_scent(self, ants):
		for xy, edge in self._edges.iteritems():
			p, Q, t = self._p, self._q, edge.phermone
			edge.phermone = (1 - p) * t + sum(Q / a.distance for a in ants if xy in a.moves)
	

class Ant(object):
	uid = 0

	def __init__(self, world, a=1, b=1, start=None):
		self._uid = Ant.uid
		Ant.uid += 1
		self._world = world
		self.alpha = a
		self.beta = b
		self._trip_complete = False
		self.reset(start)

	def clone(self):
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
		if self._node is None:
			return 1
		return 1 / float(self._world.get_distance(self._node, move))
		
	def trail_level(self, move):
		if self._node is None:
			return float(1)
		return self._world.get_scent(self._node, move)

	def log(self, msg):
		print "%s [Ant #%s] %s" % (time.time(), self._uid, msg)

	def reset(self, start=None):
		self._start = start
		self._node = start
		self._traveled = 0
		self._path = []
		self._trip_complete = False
		if start is not None:
			self._path.append(start)

	def can_move(self):
		return not self._trip_complete

	def move(self):
		moves = self.get_possible_moves()
		move = self.choose_move(moves)
		if move:
			self.make_move(move)
			if len(self._path) == len(self._world.coords):
				self._traveled += self._world.get_distance(self._path[-1], self._path[0])
				self._trip_complete = True

	def get_possible_moves(self):
		return set(self._world.coords) - set(self._path)

	def choose_move(self, moves):
		if len(moves) == 0:
			return None	# No more moves
		moves, weights = self.weigh(moves)
		cumdist = list(self._accumulate(weights))
		r = random.random() * cumdist[-1]
		i = bisect.bisect(cumdist, r)
		try:
			return moves[i]
		except IndexError as ie:
			return moves[-1]

	def _accumulate(self, iterable, func=operator.add):
		it = iter(iterable)
		total = next(it)
		yield total
		for element in it:
			total = func(total, element)
			yield total

	def weigh(self, moves):
		weighted_moves = []
		for m in moves:
			w = (m, self.calculate_weight(m))
			weighted_moves.append(w)
		return zip(*weighted_moves)

	def calculate_weight(self, move):
		n = self.attractiveness(move)
		t = self.trail_level(move)
		w = pow(n, self._a) * pow(t, self._b)
		#self.log("Weight of (%s -> %s) is %s [pre=%s, post=%s]" % (self._node, move, w, n, t))
		return w

	def make_move(self, move):
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
	world = World(TEST_COORDS, p=.6, Q=1)
	fastest = None
	niters = 100
	print "\n{:21}{:12}{:20}".format("Time Elapsed", "Trial", "Distance")
	print "-" * (25 + 12 + 20)
	start_time = time.time()
	for i, ant in enumerate(world.solve(iter_count=niters, alpha=.1, beta=1)):
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
		#print "  {:>8} ({:>3}) = ({:0.6f}, {:0.6f})".format(world.coords.index((x,y)), TEST_225_TOUR[i], x, y)
		print "  {:>8} = ({:0.6f}, {:0.6f})".format(world.coords.index((x,y)), x, y)
		i += 1
	print "Time for best solution: {}".format(timedelta(seconds=fastest_time))
	
