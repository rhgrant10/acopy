"""
.. module:: world
    :platform: Linux, Unix, Windows
    :synopsis: Provides classes for representing a world and its edges.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""
        
import json
        

class World:
    """This class contains the nodes and edges that comprise a world.

    In addition to a name and description, each world is assigned a UID.

    """
    uid = 0

    def __init__(self, nodes, lfunc=None, **kwargs):
        """Create a new world consisting of the given *nodes*.
        
        :param list nodes: a list of nodes
        :param callable lfunc: a function that calculates the distance between
                               two nodes
        :param str name: the name of the world (default is "world#", where
                         "#" is the ``uid`` of the world)
        :param str description: a description of the world (default is None)

        """
        self._nodes = nodes
        self.edges = {}
        for m, a in enumerate(nodes):
            for n, b in enumerate(nodes):
                if a != b:
                    edge = Edge(a, b, length=lfunc(a, b))
                    self.edges[m, n] = edge
        self.uid = self.__class__.uid
        self.__class__.uid += 1
        self.name = kwargs.get('name', 'world{}'.format(self.uid))
        self.description = kwargs.get('description', None)

    @property
    def nodes(self):
        """Return the IDs of all the nodes.
        """
        return list(range(len(self._nodes)))
    
    def reset_pheromone(self, level=None):
        """Reset the amount of pheromone on every edge to *level*.
        
        :param float level: amount of pheromone to set on each edge.

        """
        level = level or 0.01
        for edge in self.edges.values():
            edge.pheromone = level
        
    def data(self, idx, idy=None):
        """Return the node data of a single id or the edge data of two ids.

        :param int idx: the id of the first node
        :param int idy: the id of the second node (default is None)

        """
        
        try:
            if idy is None:
                return self._nodes[idx]
            else:
                return self.edges[idx, idy]
        except IndexError:
            return None


class Edge:
    """This class represents the link connecting two nodes.

    In addition to start and end nodes, every :class:`Edge` has a legnth and a
    pheromone level.  The length represents static, apriori information, while
    the pheromone level represents dynamic, posteriori information.

    """
    def __init__(self, a, b, length=None, pheromone=None):
        """Create a new :class:`Edge` between *a* and *b*.

        :param Node a: the node at the start of the :class:`Edge`
        :param Node b: the node at the end of the :class:`Edge`
        :param float length: the length of the :class:`Edge` (default=1)
        :param float pheromone: the amount of pheromone on the :class:`Edge` 
                                (default=0.1)

        """
        self.start = a
        self.end = b
        self.length = 1 if length is None else length
        self.pheromone = 0.1 if pheromone is None else pheromone

    def __eq__(self, other):
        """Return ``True`` iff *other* has identical properties.

        Two :class:`Edge`s are **not** equal if their lengths or pheromone
        level differs.

        :rtype: bool

        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
        
