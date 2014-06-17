from ..world import World, Edge
import unittest
import math

class WorldTest(unittest.TestCase):
    def setUp(self):
        self.nodeA = dict(name="A")
        self.nodeB = dict(name="B")
        self.nodeC = dict(name="C")
        self.edgeAB = Edge(self.nodeA, self.nodeB)
        self.edgeBA = Edge(self.nodeB, self.nodeA)
        self.edgeAC = Edge(self.nodeA, self.nodeC)
        self.edgeCA = Edge(self.nodeC, self.nodeA)
        self.edgeBC = Edge(self.nodeB, self.nodeC)
        self.edgeCB = Edge(self.nodeC, self.nodeB)
        self.edgeAB2 = Edge(self.nodeA, self.nodeB,
            length=self.edgeAB.length + 1)

class WorldCreation(WorldTest):
    def test_world_creation_with_no_arguments(self):
        w = World()
        self.assertEqual(w.nodes, [])
        self.assertEqual(w.edges, {})
        
    def test_world_creation_from_edge_list(self):
        edges = [self.edgeAB, self.edgeBA]
        w = World(edges)
        self.assertEqual(len(w.nodes), 2)

    def test_world_creation_failure_from_list_of_nonedges(self):
        not_edges = {"Not", "an", "edge", "list"}
        self.assertRaises(TypeError, World, (not_edges,))
    
    def test_world_creation_failure_from_extra_kwargs(self):
        self.assertRaises(TypeError, World, unknown="keyword")
        
    def test_world_creation_failure_from_extra_args(self):
        self.assertRaises(TypeError, World, (1,2,3))
    
    
class EdgeAddition(WorldTest):
    def test_world_correct_edge_count(self):
        w = World()
        w.add_edge(self.edgeAB)
        w.add_edge(self.edgeBA)
        self.assertEqual(len(w.edges), 2, "Wrong number of edges added")

    def test_world_no_duplicate_nodes(self):
        w = World()
        w.add_edge(self.edgeAB)
        w.add_edge(self.edgeAC)
        self.assertEqual(len(w.nodes), 3, "Wrong number of nodes extracted")
        
    def test_world_edge_replacement(self):
        w = World()
        w.add_edge(self.edgeAB)
        w.add_edge(self.edgeAB2)
        self.assertEqual(len(w.edges), 1)
        self.assertEqual(w.edges[0, 1], self.edgeAB2)
        

class PheromoneReset(WorldTest):
    def test_world_pheromone_level_of_every_edge_reset(self):
        edges = [self.edgeAB, self.edgeBA]
        w = World(edges)
        p = 1234
        w.reset_pheromone(p)
        self.assertTrue(all(e.pheromone == p for e in w.edges.values()))
        
    def test_world_pheromone_can_never_be_zero(self):
        edges = [self.edgeAB, self.edgeBA]
        w = World(edges)
        p = 0
        w.reset_pheromone(p)
        self.assertTrue(all(e.pheromone > 0 for e in w.edges.values()))
        

class EdgeTest(unittest.TestCase):
    def setUp(self):
        self.nodeA = dict(name="A")
        self.nodeB = dict(name="B")
        self.nodeC = dict(name="C")


class EdgeCreation(EdgeTest):        
    def test_edge_creation_with_no_args(self):
        self.assertRaises(TypeError, Edge)
        
    def test_edge_creation_with_mutable_nodes(self):
        self.assertRaises(TypeError, Edge, ({}, {}))
        
    def test_edge_creation_with_immutable_nodes(self):
        e = Edge(self.nodeA, self.nodeB)
        self.assertEqual(e.start, self.nodeA)
        self.assertEqual(e.end, self.nodeB)
        
    def test_edge_creation_with_custom_length(self):
        length = 100
        e = Edge(self.nodeA, self.nodeB, length=length)
        self.assertEqual(e.length, length)
        
    def test_edge_creation_with_custom_pheromone_level(self):
        level = 100
        e = Edge(self.nodeA, self.nodeB, pheromone=level)
        self.assertEqual(e.pheromone, level)


class EdgeEquality(EdgeTest):
    def test_edge_identical_edge_equality(self):
        e1 = Edge(self.nodeA, self.nodeB)
        e2 = Edge(self.nodeA, self.nodeB)
        self.assertEqual(e1, e2)
        
    def test_edge_length_difference_inequality(self):
        e1 = Edge(self.nodeA, self.nodeB, length=1)
        e2 = Edge(self.nodeA, self.nodeB, length=2)
        self.assertNotEqual(e1, e2)
        
    def test_edge_pheromone_difference_inequality(self):
        e1 = Edge(self.nodeA, self.nodeB, pheromone=1)
        e2 = Edge(self.nodeA, self.nodeB, pheromone=2)
        self.assertNotEqual(e1, e2)
        
    def test_edge_node_difference_inequality(self):
        e1 = Edge(self.nodeA, self.nodeB)
        e2 = Edge(self.nodeB, self.nodeA)
        self.assertNotEqual(e1, e2)
            
            
if __name__ == '__main__':
    unittest.main()