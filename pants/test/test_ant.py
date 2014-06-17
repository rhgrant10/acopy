from ..ant import Ant
from ..world import World, Edge
import unittest
import unittest.mock

class AntTest(unittest.TestCase):
    @unittest.mock.patch('__main__.World')
    def setUp(self, MockWorld):
        self.nodeA = dict(name='a')
        self.nodeB = dict(name='b')
        self.world = World()
        self.aa = 1
        self.ab = 3
        self.ba = 5
        self.edgeAA = Edge(self.nodeA, self.nodeA, length=self.aa)
        self.edgeAB = Edge(self.nodeA, self.nodeB, length=self.ab)
        self.edgeBA = Edge(self.nodeB, self.nodeA, length=self.ba)
        self.edgeNoLength = Edge(self.nodeA, self.nodeB, length=0)
        self.edgeNoPheromone = Edge(self.nodeA, self.nodeB, length=1, pheromone=0)
        self.edge1and1 = Edge(self.nodeA, self.nodeB, 1, 1)

    def test_ant_uids_increase_by_one(self):
        n = 10
        uids = [Ant(self.world).uid for _ in range(n)]
        for i in range(n - 1):
            self.assertTrue(uids[i] + 1 == uids[i + 1])
    
    def test_ant_make_move_adds_no_distance_when_moving_to_start_node(self):
        self.world.add_edge(self.edgeAB)
        ant = Ant(self.world)
        ant.make_move(0)
        self.assertEqual(ant.distance, 0)

    def test_ant_make_move_accounts_for_distance_to_start_node(self):
        def get_edge(pair):
            d = {
                (0, 1): self.edgeAB,
                (1, 0): self.edgeBA
            }
            return d.get(pair, None)
        self.world.edges.__getitem__.side_effect = get_edge
        self.world.nodes = [0, 1]
        ant = Ant(self.world, start=0)
        ant.make_move(1)
        self.assertEqual(ant.distance, self.ab + self.ba)
                
    def test_ant_possible_moves_is_b_when_b_is_only_move_left(self):
        self.world.nodes = [0, 1]
        self.world.edges.__getitem__.side_effect = lambda x: self.edgeAB
        ant = Ant(self.world, start=0)
        moves = list(ant.get_possible_moves())
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0], 1)
        
    def test_ant_possible_moves_is_empty_when_no_moves_left(self):
        self.world.nodes = [0]
        self.world.edges.__getitem__.side_effect = lambda x: self.edgeAA
        ant = Ant(self.world, start=0)
        moves = list(ant.get_possible_moves())
        self.assertEqual(len(moves), 0)
    
    def test_ant_choose_move_returns_b_when_b_is_only_move(self):
        self.world.edges.__getitem__.return_value = self.edgeAB
        ant = Ant(self.world, start=0)
        move = ant.choose_move([1])
        self.assertEqual(move, 1)
    
    def test_ant_choose_move_returns_None_when_no_moves(self):
        self.world.add_edge(self.edgeAB)
        ant = Ant(self.world, start=0)
        move = ant.choose_move([])
        self.assertEqual(move, None)

    def test_ant_calculate_weight_when_edge_length_is_zero(self):
        ant = Ant(self.world, alpha=1, beta=1)
        weight = ant.calculate_weight(self.edgeNoLength)
        self.assertEqual(self.edgeNoLength.pheromone, weight)
        
    def test_ant_calculate_weight_when_edge_pheromone_is_zero(self):
        ant = Ant(self.world, alpha=1, beta=1)
        weight = ant.calculate_weight(self.edgeNoPheromone)
        self.assertEqual(weight, 0)
        
    def test_ant_clone_has_equal_properties_after_moving(self):
        self.world.add_edge(self.edgeAB)
        self.world.add_edge(self.edgeBA)
        ant = Ant(self.world)
        ant.move()
        clone = ant.clone()
        self.assertEqual(ant.alpha, clone.alpha)
        self.assertEqual(ant.beta, clone.beta)
        self.assertEqual(ant.start, clone.start)
        self.assertEqual(ant.node, clone.node)
        self.assertEqual(ant.distance, clone.distance)
        self.assertEqual(ant.path, clone.path)
        self.assertEqual(ant.uid, clone.uid)

    def test_ant_clone_has_equal_properties_before_moving(self):
        ant = Ant(self.world)
        clone = ant.clone()
        self.assertEqual(ant.alpha, clone.alpha)
        self.assertEqual(ant.beta, clone.beta)
        self.assertEqual(ant.start, clone.start)
        self.assertEqual(ant.node, clone.node)
        self.assertEqual(ant.distance, clone.distance)
        self.assertEqual(ant.path, clone.path)
        self.assertEqual(ant.uid, clone.uid)
        

if __name__ == '__main__':
    unittest.main()