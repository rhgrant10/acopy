from ..ant import Ant
from ..world import World, Edge, Node
from ..solver import Solver

import unittest
from unittest import mock

class SolverTest(unittest.TestCase):
    def setUp(self):
        self.nodes = [Node(name='a'), Node(name='b')]
        self.world = mock.Mock(World)
        self.world.nodes = self.nodes[:]
        
    def test_random_ants_when_even_and_ant_count_less_than_node_count(self):
        freq = 2
        node_count = len(self.nodes)
        ant_count = node_count // freq
        solver = Solver(self.world, ant_count=ant_count)
        
        ants = solver.random_ants(even=True)
        
        ants_on = dict.fromkeys(self.nodes, 0)
        for a in ants:
            self.assertFalse(a.start is None,
                    "At least one ant was not placed on a node to start"
                    )
            ants_on[a.start] += 1
        
        self.assertFalse(any(c > 1 for c in ants_on.values()),
                "More than one ant was placed on the same node to start"
                )
        
    def test_random_ants_when_even_and_ant_count_exceeds_node_count(self):
        freq = 2
        node_count = len(self.nodes)
        ant_count = freq * node_count
        solver = Solver(self.world, ant_count=ant_count)
        
        ants = solver.random_ants(even=True)
        
        ants_on = dict.fromkeys(self.nodes, 0)
        for a in ants:
            self.assertFalse(a.start is None,
                    "At least one ant was not placed on a node to start"
                    )
            ants_on[a.start] += 1
        
        self.assertTrue(all(c == freq for c in ants_on.values()),
                "Ants were not placed on nodes to start evenly")
        self.assertEqual(sum(ants_on.values()), ant_count,
                "Not all ants were placed on a node to start")
        
        
if __name__ == '__main__':
    unittest.main()