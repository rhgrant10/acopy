from ..world import World, Edge
import unittest
import math

class WorldTest(unittest.TestCase):
    known_distances = [
        (( 0,  0), ( 0,  1), 1),
        (( 0,  0), ( 1,  0), 1),
        (( 0,  1), ( 0,  0), 1),
        (( 1,  0), ( 0,  0), 1),
        (( 0,  0), ( 0, -1), 1),
        (( 0,  0), (-1,  0), 1),
        (( 0, -1), ( 0,  0), 1),
        ((-1,  0), ( 0,  0), 1),
        (( 0,  0), ( 3,  4), 5),
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
        for i, j, d in self.known_distances:
            self.assertEqual(Edge.distance(i, j), d)
    
    def test_world_euclidean_edges(self):
        edges = World.euclidean_edges(self.coords)
        for i, j, d in self.euclidean_answers:
            self.assertEqual(edges[self.coords[i], self.coords[j]].distance, d)
            self.assertEqual(edges[self.coords[j], self.coords[i]].distance, d)

    def test_world_edge_distance(self):
        co = (0, 0), (0, 3)
        edges = {
            co: Edge(*co)
        }
        world = World(co, edges)
        self.assertEqual(world.distance(*co), 3)

    def test_world_nonexistent_edge(self):
        co = (0, 0), (0, 3)
        edges = {
            co: Edge(*co)
        }
        world = World(co, edges)
        self.assertEqual(world.distance((0, 0), (0, 4)), -1)
        self.assertEqual(world.scent((0, 0), (0, 4)), 0)
            
if __name__ == '__main__':
    unittest.main()
