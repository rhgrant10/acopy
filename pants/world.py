"""
.. module:: world
    :platform: Linux, Unix, Windows
    :synopsis: Provides classes for representing a world and its edges.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""
        
import json
        

class World:
    def __init__(self, edges=None):
        """Create a new world consisting of the given *edges*.
        
        :param list edges: a list of :class:`Edge`s

        """
        self._nodes = set()
        self.edges = {}
        if edges is not None:
            for e in edges:
                self.add_edge(e)
                
    @property
    def nodes(self):
        return list(self._nodes)
    
    def reset_pheromone(self, level=None):
        """Reset the amount of pheromone on every edge to *level*.
        """
        level = level or 0.01
        for edge in self.edges.values():
            edge.pheromone = level
        
    def add_edge(self, edge):
        """Add *edge* to the :class:`World`.
        
        :param :class:`Edge` edge: the :class:`Edge` to add
        
        """
        if not isinstance(edge, Edge):
            raise TypeError("edge must be <type Edge>")
        self._nodes.add(edge.start)
        self._nodes.add(edge.end)
        self.edges[edge.start, edge.end] = edge    
        
    

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
        
    def __repr__(self):
        return "Edge from {} to {} that is {} long.".format(
                self.start, self.end, self.length)
        
    def __eq__(self, other):
        """Return ``True`` iff *other* has identical properties.

        Two :class:`Edge`s are **not** equal if their lengths or pheromone
        level differs.

        :rtype: bool

        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
        
        
class Node:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._hash = None
        
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self.__dict__.items()))
        return self._hash
            
    def __bool__(self):
        return True
      
    # 
    def __repr__(self):
        return json.dumps(
            {k:v for k,v in self.__dict__.items() if not k.startswith("_")},
            default=str)
        
    # Returns true iff other is the same type and has identical "public"
    # properties.
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            sd = {k:v for k, v in self.__dict__.items() if not k.startswith("_")}
            od = {k:v for k, v in other.__dict__.items() if not k.startswith("_")}
            return sd == od
        return False