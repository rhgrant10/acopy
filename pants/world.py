import math

class World:
    def __init__(self, coords, edges=None):
        """
        Create a new world consisting of the given coordinates.

        The world is defined by a set of (x, y) coordinates, the assumption
        that each point can be reached from every other point, and a few
        other variables.

        Parameters:
            coords - list of (x, y) coordinates
            edges - dict of Edge instances with node-pair tuples as keys

        """
        self.coords = coords
        self.edges = edges or self.create_map()
        
    def create_map(self):
        """
        Create a map of the world from the coordinates.
        """
        edges = {}
        for a in self.coords:
            for b in self.coords:
                edges[a, b] = Edge(a, b)
                edges[b, a] = Edge(b, a, dist=edges[a, b].distance)
        return edges

    def distance(self, a, b):
        """
        Return the distance of the edge between a and b.
        """
        e = self.edges.get((a, b), None)
        return e.distance if e is not None else 0

    def scent(self, a, b):
        """
        Return the amount of pheromone on the edge between a and b.
        """
        e = self.edges.get((a, b), None)
        return e.pheromone if e is not None else 0


class Edge:
    """
    The connection between to coordinates.

    Each edge is composed of a distance and an amount of pheromone.

    """
    def __init__(self, a, b, dist=None, pheromone=0.1):
        """
        Create a new Edge between a and b.

        Parameters:
            a - the start of the edge
            b - the end of the edge
            dist - the distance between a and b (defaults to Euclidean)
            pheromone - the initial amount of pheromone (defaults to 0.1)

        """
        self.start = a
        self.end = b
        self.distance = Edge.distance(a, b) if dist is None else dist
        self.pheromone = 0.1 if pheromone is None else pheromone

    @staticmethod
    def distance(a, b):
        """
        Return the Euclidean distance between a and b.

        Parameters:
            a - the first point (x1, y1)
            b - the second point (x2, y2)
        Returns:
            sqrt((x2 - x1)^2 + (y2 - y1)^2)

        """
        x = b[0] - a[0]
        y = b[1] - a[1]
        return math.sqrt(x*x + y*y)
        
        
