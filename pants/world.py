import math

class World:
    def __init__(self, nodes=None, edges=None):
        """
        Create a new world consisting of the given coordinates.

        The world is defined by a set of (x, y) coordinates, the assumption
        that each Node can be reached from every other Node, and a few
        other variables.

        Parameters:
            nodes - list of Nodes
            edges - list of Edges 

        """
        self.nodes = [] if nodes is None else nodes
        self.edges = {} if edges is None else edges

    @classmethod
    def Euclidean(cls, nodes):
        edges = {(a, b): Edge(a, b) for a in nodes for b in nodes}
        return cls(nodes, edges)


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
        self.distance = a.distance(b) if dist is None else dist
        self.pheromone = 0.1 if pheromone is None else pheromone

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False
        

class Node:
    """
    A 2D Node.
    """
    def __init__(self, x=0, y=0):
        """
        Create a new Node.
        """
        self.x = x
        self.y = y

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False
        
    def __repr__(self):
        return "({}, {})".format(self.x, self.y)
        
    def __iter__(self):
        yield self.x
        yield self.y
        
    def __format__(self, spec):
        return "({1:{0}}, {2:{0}})".format(spec, float(self.x), float(self.y))

    def __add__(self, other):
        return self.__class__(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        return self.__class__(x=self.x - other.x, y=self.y - other.y)

    def distance(self, other=None):
        """
        Return the distance to the other Node (defaults to origin).
        """
        if other is None:
            other = self.__class__()
        return math.sqrt(pow(other.x - self.x, 2) + pow(other.y - self.y, 2))

