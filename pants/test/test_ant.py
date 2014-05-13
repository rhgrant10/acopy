from ..ant import Ant
import unittest
from unittest import mock

class AntTest(unittest.TestCase):
	def setUp(self):
		# TODO: Mock the world object
		coords = [(0, 0), (1, 1), (0, 2)]
		self.world = World(coords)
		
	def test_uid_behavior(self):
		n = 5
		base_uid = Ant(self.world).uid
		upper_uid = base_uid + 5
		expected_uids = range(base_uid, upper_uid)
		uids = [Ant(world).uid for i in range(n)]
		self.assertEqual(expected_uids, uids)

	def test_initial_properties(self):
		pass

	def test_moves(self):
		pass

	def test_clone_equality(self):
		pass

	def test_distance_ordering(self):
		pass

	def test_reset(self):
		pass

	def test_can_move(self):
		pass

	def test_get_possible_moves(self):
		pass

	def test_choose_move(self):
		pass

	def test_calculate_weight(self):
		pass

	def test_make_move(self):
		pass

	def test_move(self):
		pass

	def tearDown(self):
		del self.world


if __name__ == '__main__':
	unittest.main()