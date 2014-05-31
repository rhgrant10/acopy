"""
.. module:: world
    :platform: Linux, Unix, Windows
    :synopsis: Provides classes for representing a world including its nodes
               and edges.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""

import math

class World:
    def __init__(self, nodes=None, edges=None):
        """Create a new world consisting of *nodes* and *edges*

        This is the most direct way of creating a :class:`World`. Currently,
        you must create the :class:`Edge` mapping yourself:
        
        .. code::python

            edges = {(a, b): Edge(a, b) for a in nodes for b in nodes}

        TODO: let the user pass in a simple list of :class:`Edge`s and 
              construct the mapping automatically.

        :param list nodes: the :class:`Node`s of the :class:`World`
        :param dict edges: mapping of :class:`Node` pairs to :class:`Edge`s

        """
        self.nodes = [] if nodes is None else nodes
        self.edges = {} if edges is None else edges

    @classmethod
    def Euclidean(cls, nodes):
        """Create a :class:`World` in which there is an :class:`Edge` between
        each possible pair of :class:`Node`s with distances goverened by the
        Euclidean distance formula.

        :param list nodes: the :class:`Node`s of the :class:`World`

        :returns: a Euclidean :class:`World`
        :rtype: :class:`World`

        """
        edges = {(a, b): Edge(a, b) for a in nodes for b in nodes}
        return cls(nodes, edges)


class Edge:
    """This class represents the link connecting two :class:`Node`s.

    Each :class:`Edge` is composed of start and end :class:`Node`s, as well as
    a length and an amount of pheromone.

    TODO: refactor *distance* to *length* (makes more sense).

    """
    def __init__(self, a, b, dist=None, pheromone=0.1):
        """Create a new :class:`Edge` between *a* and *b*.

        :param Node a: the starting :class:`Node`
        :param Node b: the ening :class:`Node`
        :param float dist: the length of the :class:`Edge` (defaults to 
                           Euclidean)
        :param float pheromone: the amount of pheromone (default=0.1)

        """
        self.start = a
        self.end = b
        self.distance = a.distance(b) if dist is None else dist
        self.pheromone = 0.1 if pheromone is None else pheromone

    def __eq__(self, other):
        """Return ``True`` iff *other* has identical properties.

        Two :class:`Edge`s are **not** equal if their distances or pheromone
        level differs.

        :rtype: bool

        """
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False
        

class Node:
    """This class represents a two dimensional node.
    
    """
    def __init__(self, x=0, y=0):
        """Create a new :class:`Node` with *x* and *y* coordinates.

        :param float x: the horizontal component
        :param float y: the vertical component

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
        """Iterate over the x and y components.

        This allows for unpacking the compnents:

        .. code::pythoon
            for x, y in node:
                ...

        :returns: both x annd y components

        """
        yield self.x
        yield self.y
        
    def __format__(self, spec):
        return "({1:{0}}, {2:{0}})".format(spec, float(self.x), float(self.y))

    def __add__(self, other):
        return self.__class__(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other):
        return self.__class__(x=self.x - other.x, y=self.y - other.y)

    def distance(self, fro=None):
        """Return the distance from another :class:`Node` (defaults to origin).

        :param Node fro: the node from which to calculate the distance (default
                         is from the origin)

        :returns: Euclidean distance from *fro* or the origin if *fro* is not
                  given
        :rtype: float

        """
        if fro is None:
            fro = self.__class__()
        return math.sqrt(pow(fro.x - self.x, 2) + pow(fro.y - self.y, 2))

