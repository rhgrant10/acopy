from ..ant import Ant
from ..world import World
import unittest

class AntTest(unittest.TestCase):
    def setUp(self):
        # TODO: Mock the world object
        self.coords = [(0, 0), (1, 1), (0, 2)]
        self.world = World(self.coords)
        
    def test_uid_behavior(self):
        n = 5
        base_uid = Ant(self.world).uid + 1
        expected_uids = list(range(base_uid, base_uid + n))
        uids = [Ant(self.world).uid for i in range(n)]
        self.assertEqual(expected_uids, uids)

    def test_initial_properties(self):
        ant = Ant(self.world)
        self.assertFalse(ant.trip_complete)
        self.assertEqual(ant.distance, 0)
        self.assertEqual(len(ant.moves), 0)

    def test_moves(self):
        # TODO: Add case where len(ant.path) == 1
        ant = Ant(self.world)
        ant.path = self.world.coords[:2]
        expected_moves = [
            (self.world.coords[0], self.world.coords[1]),
            (self.world.coords[1], self.world.coords[0])
        ]
        self.assertEqual(ant.moves, expected_moves)
        
    def test_clone_equality(self):
        # TODO: mock world.distance
        # TODO: mock ant.get_possible_moves
        # TODO: mock ant.choose_move
        ant = Ant(self.world, start=self.world.coords[0])
        ant.move()
        clone = ant.clone()
        self.assertEqual(ant.uid, clone.uid)
        self.assertEqual(ant.distance, clone.distance)
        self.assertEqual(ant.path, clone.path)
        self.assertEqual(ant.trip_complete, clone.trip_complete)
        self.assertEqual(ant.node, clone.node)
        self.assertEqual(ant.start, clone.start)
        
    def test_distance_ordering(self):
        ant1 = Ant(self.world)
        ant2 = Ant(self.world)
        ant1.distance = 1
        ant2.distance = 2
        self.assertTrue(ant1 < ant2)

    def test_reset(self):
        ant = Ant(self.world)
        start = ant.start = (10, 10)
        node = ant.node = (20, 20)
        distance = ant.distance = 30
        path = ant.path = [start, node]
        ant.reset()
        self.assertNotEqual(ant.start, start)
        self.assertNotEqual(ant.node, node)
        self.assertNotEqual(ant.distance, distance)
        self.assertNotEqual(ant.path, path)

    def test_can_move(self):
        ant = Ant(self.world)
        self.assertTrue(ant.can_move())
        ant = Ant(World(list()))
        self.assertFalse(ant.can_move())
        # TODO: mock ant.get_possible_moves, then call:
        #self.assertFalse(ant.can_move())

    def test_get_possible_moves(self):
        ant = Ant(self.world)
        self.assertEqual(list(ant.get_possible_moves()), self.world.coords)
        ant = Ant(World(list()))
        self.assertEqual(list(ant.get_possible_moves()), [])

    def test_choose_move(self):
        # TODO: case where no moves exist
        # TODO: case where only one move exists
        # TODO: case where many moves exist
        pass

    def test_calculate_weight(self):
        ant = Ant(self.world, alpha=2, beta=3)
        self.assertEqual(ant.calculate_weight(1, 1), 1)
        self.assertEqual(ant.calculate_weight(2, 1), 8)
        self.assertEqual(ant.calculate_weight(1, 2), 4)

    def test_make_move(self):
        # TODO: mock world.distance
        edge = self.world.edges[self.coords[0], self.coords[1]]
        ant = Ant(self.world, start=edge.start)
        path_length = len(ant.path)
        ant.make_move(edge.end)
        self.assertEqual(ant.distance, edge.distance)
        self.assertEqual(len(ant.path), path_length + 1)
        self.assertEqual(ant.path[-2], edge.start)
        self.assertEqual(ant.path[-1], edge.end)
        self.assertEqual(ant.node, edge.end)

    def test_move(self):
        ant = Ant(self.world)
        # TODO: case where there are no moves to make
        # TODO: case where there is a single move to make
        # TODO: case where there are many moves to make
        # TODO: case where move to make is the last move possible
        
    def tearDown(self):
        del self.world
        del self.coords


if __name__ == '__main__':
    unittest.main()