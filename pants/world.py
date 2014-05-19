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
        if edges is None:
            edges = World.euclidean_edges(coords)
        self.edges = {(e.start, e.end): e for e in edges}
    
    @staticmethod
    def euclidean_edges(coords):
        """
        Create a map of the world from the coordinates.
        """
        return [Edge(a, b) for a in coords for b in coords]
        
    def distance(self, a, b):
        """
        Return the distance of the edge between a and b.
        """
        e = self.edges.get((a, b), None)
        return e.distance if e is not None else -1

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
        return math.sqrt(pow(b.x - a.x, 2) + pow(b.y - a.y, 2))
        
    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False
        

class Node:
    def __init__(self, x=0, y=0, data=None):
        self.x = x
        self.y = y
        self.data = {} if data is None else data
        
    @classmethod
    def from_data(cls, data, getx=None, gety=None):
        if getx is None or not callable(getx):
            getx = lambda d: d['x']
        if gety is None or not callable(gety):
            gety = lambda d: d['y']
        return cls(x=getx(data), y=gety(data), data=data)

    def __getitem__(self, key):
        return self.data.get(key, None)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False
        