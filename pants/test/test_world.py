from ..world import World, Edge
import unittest

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
    
    def test_edge_distance(self):
        for (a, b), d in self.known_distances:
            e = Edge(a, b)
            self.assertEqual(e.distance, d)
            
            
if __name__ == '__main__':
    unittest.main()