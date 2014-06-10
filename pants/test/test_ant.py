from ..ant import Ant
from ..world import World, Edge, Node
import unittest
import unittest.mock

class AntTest(unittest.TestCase):
    def setUp(self):
        self.nodeA = Node(name='a')
        self.nodeB = Node(name='b')
        self.world = World()
        self.aa = 1
        self.ab = 3
        self.ba = 5
        self.edgeAA = Edge(self.nodeA, self.nodeA, length=self.aa)
        self.edgeAB = Edge(self.nodeA, self.nodeB, length=self.ab)
        self.edgeBA = Edge(self.nodeB, self.nodeA, length=self.ba)

    @unittest.mock.patch('__main__.World')
    def test_ant_uid_increases_by_one(self, MockWorld):
        n = 10
        uids = [Ant(self.world).uid for _ in range(n)]
        for i in range(n - 1):
            self.assertTrue(uids[i] + 1 == uids[i + 1])
    
    # TODO: Mock Node, Edge, and World
    def test_ant_make_move_adds_no_distance_when_moving_to_start_node(self):
        self.world.add_edge(self.edgeAB)
        ant = Ant(self.world)

        ant.make_move(self.nodeA)

        self.assertEqual(ant.distance, 0)

    def test_ant_make_move_accounts_for_distance_to_start_node(self):
        self.world.add_edge(self.edgeAB)
        self.world.add_edge(self.edgeBA)
        ant = Ant(self.world, start=self.nodeA)

        ant.make_move(self.nodeB)

        self.assertEqual(ant.distance, self.ab + self.ba)
                
    def test_ant_possible_moves_is_b_when_b_is_only_move_left(self):
        self.world.add_edge(self.edgeAB)
        ant = Ant(self.world, start=self.nodeA)

        moves = list(ant.get_possible_moves())

        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0], self.nodeB)
        
    def test_ant_possible_moves_is_empty_when_no_moves_left(self):
        self.world.add_edge(self.edgeAA)
        ant = Ant(self.world, start=self.nodeA)

        moves = list(ant.get_possible_moves())        

        self.assertEqual(len(moves), 0)
    
    def test_ant_choose_move_returns_b_when_b_is_only_move(self):
        self.world.add_edge(self.edgeAB)
        ant = Ant(self.world, start=self.nodeA)

        move = ant.choose_move([self.nodeB])

        self.assertEqual(move, self.nodeB)
    
    def test_ant_choose_move_returns_None_when_no_moves(self):
        self.world.add_edge(self.edgeAB)
        ant = Ant(self.world, start=self.nodeA)

        move = ant.choose_move([])

        self.assertEqual(move, None)


if __name__ == '__main__':
    unittest.main()