from ..world import World, Edge
import unittest
import math

class WorldTest(unittest.TestCase):
    known_distances = [
        ((( 0,  0), ( 0,  1)), 1),
        ((( 0,  0), ( 1,  0)), 1),
        ((( 0,  1), ( 0,  0)), 1),
        ((( 1,  0), ( 0,  0)), 1),
        ((( 0,  0), ( 0, -1)), 1),
        ((( 0,  0), (-1,  0)), 1),
        ((( 0, -1), ( 0,  0)), 1),
        (((-1,  0), ( 0,  0)), 1),
        ((( 0,  0), ( 3,  4)), 5),
    ]
    
    coords = [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
    ]
    
    euclidean_answers = [
        (0, 1, 1),
        (0, 2, 2),
        (0, 3, 1),
        (1, 2, 1),
        (1, 3, math.sqrt(2)),
        (2, 3, math.sqrt(5))
    ]
        
    def test_edge_distance(self):
        for (a, b), d in self.known_distances:
            e = Edge(a, b)
            self.assertEqual(e.distance, d)
    
    def test_world_euclidean_edges(self):
        edges = World.euclidean_edges(self.coords)
        for i, j, d in self.euclidean_answers:
            self.assertEqual(edges[self.coords[i], self.coords[j]].distance, d)
            self.assertEqual(edges[self.coords[j], self.coords[i]].distance, d)
    
            
if __name__ == '__main__':
    unittest.main()
