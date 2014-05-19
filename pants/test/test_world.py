from ..world import World, Edge
import unittest
import math

class EdgeTest(unittest.TestCase):
    def setUp(self):
        self.edges = [
            (( 0,  0), ( 0,  1)),
            (( 0,  0), ( 1,  0)),
            (( 0,  1), ( 0,  0)),
            (( 1,  0), ( 0,  0)),
            (( 0,  0), ( 0, -1)),
            (( 0,  0), (-1,  0)),
            (( 0, -1), ( 0,  0)),
            ((-1,  0), ( 0,  0)),
            (( 0,  0), ( 3,  4)),
        ]
        self.distances = [1, 1, 1, 1, 1, 1, 1, 1, 5]

    def test_static_edge_distance(self):
        for (c1, c2), d in zip(self.edges, self.distances):
            self.assertEqual(Edge.distance(c1, c2), d)

    def test_default_edge_distance(self):
        edges = [Edge(a, b) for a, b in self.edges]
        for i, e in enumerate(edges):
            self.assertEqual(e.distance, self.distances[i])
            
    def test_default_pheromone_equality(self):
        edges = [Edge(a, b) for a, b in self.edges]
        for e in edges[1:]:
            self.assertEqual(e.pheromone, edges[0].pheromone)
            
    def tearDown(self):
        del self.edges
        del self.distances


class WorldTest(unittest.TestCase):
    def setUp(self):
        self.coords = [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 0),
        ]

        # TODO: mock (static) Edge.distance
        self.edges = [
            Edge(a, b) for a in self.coords for b in self.coords
        ]
        
        self.world = World(self.coords, self.edges)        
        
        self.cases = [
            (0, 0, 0),
            (0, 1, 1),
            (0, 2, 2),
            (0, 3, 1),
            (1, 2, 1),
            (1, 3, math.sqrt(2)),
            (2, 3, math.sqrt(5))
        ]
        
        self.no_edge_case = [
            (-1, -1), (0, 0)
        ]
    
    def test_world_distance(self):
        for i, j, d in self.cases:
            a, b = self.coords[i], self.coords[j]
            self.assertEqual(self.world.distance(a, b), d)
            
    def test_world_distance_no_edge(self):
        self.assertEqual(self.world.distance(*self.no_edge_case), -1)

    def test_world_scent_no_edge(self):
        self.assertEqual(self.world.scent(*self.no_edge_case), 0)

    def tearDown(self):
        del self.no_edge_case
        del self.cases
        del self.world
        del self.edges
        del self.coords


class EuclideanWorldTest(unittest.TestCase):
    def setUp(self):
        self.coords = [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 0),
        ]
        self.edges = [Edge(a, b) for a in self.coords for b in self.coords]
        
    def test_world_euclidean_edges(self):
        edges = World.euclidean_edges(self.coords)
        self.assertEqual(self.edges, edges)
        #for i, j, d in self.euclidean_answers:
        #    self.assertEqual(edges[self.coords[i], self.coords[j]].distance, d)
        #    self.assertEqual(edges[self.coords[j], self.coords[i]].distance, d)
    
    def tearDown(self):
        del self.coords
        del self.edges
        
        
class NodeConstructorTest(unittest.TestCase):
    def setUp(self):
        self.coords = [(1,1), (3,4)]
        self.names = ['a', 'b']
        
    def test_default_constructor(self):
        n = Node()
        self.assertEqual(n.x, 0)
        self.assertEqual(n.y, 0)
        
    def test_x_and_y_constructor(self):
        for x, y in self.coords:
            n = Node(x, y)
            self.assertEqual(n.x, x)
            self.assertEqual(n.y, y)
        
    def test_tuple_constructor(self):
        for c in self.coords:
            n = Node.from_tuple(c)
            self.assertEqual(n.x, c[0])
            self.assertEqual(n.y, c[1])

    def test_dict_constructor(self):
        for (x, y), name in zip(self.coords, self.names):
            d = dict(x=x, y=y, name=name)
            n = Node.from_dict(d)
            self.assertEqual(n.x, x)
            self.assertEqual(n.y, y)
            self.assertEqual(n.get('name'), name)
            
        for (x, y), name in zip(self.coords, self.names):
            d = dict(lat=x, lng=y, name=name)
            n = Node.from_dict(d, x_name='lat', y_name='lng')
            
            
if __name__ == '__main__':
    unittest.main()
