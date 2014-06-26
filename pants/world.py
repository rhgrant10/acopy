"""
.. module:: world
    :platform: Linux, Unix, Windows
    :synopsis: Provides classes for representing a world and its edges.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""
        
import json

class World:
    """The nodes and edges of a particular problem.

    Each :class:`World` is created from a list of nodes, a length function, and
    optionally, a name and a description. Additionally, each :class:`World` has
    a UID. The length function must accept nodes as its first two parameters,
    and is responsible for returning the distance between them. It is the 
    responsibility of the :func:`create_edges` to generate the required
    :class:`Edge`\s and initialize them with the correct *length* as returned
    by the length function.
    
    Once created, :class:`World` objects convert the actual nodes into node
    IDs, since solving does not rely on the actual data in the nodes. These are
    accessible via the :attr:`nodes` property. To access the actual nodes,
    simply pass an ID obtained from :attr:`nodes` to the :func:`data` method,
    which will return the node associated with the specified ID.
    
    :class:`Edge`\s are accessible in much the same way, except two node IDs
    must be passed to the :func:`data` method to indicate which nodes start and
    end the :class:`Edge`. For example:
    
    .. code-block:: python
    
        ids = world.nodes
        assert len(ids) > 1
        node0 = world.data(ids[0])
        node1 = world.data(ids[1])
        edge01 = world.data(ids[0], ids[1])
        assert edge01.start == node0
        assert edge01.end == node1
    
    The :func:`reset_pheromone` method provides an easy way to reset the
    pheromone levels of every :class:`Edge` contained in a :class:`World` to a
    given *level*. It should be invoked before attempting to solve a 
    :class:`World` unless a "blank slate" is not desired. Also note that it
    should *not* be called between iterations of the :class:`Solver` because it
    effectively erases the memory of the :class:`Ant` colony solving it.
        
    :param list nodes: a list of nodes
    :param callable lfunc: a function that calculates the distance between
                           two nodes
    :param str name: the name of the world (default is "world#", where
                     "#" is the ``uid`` of the world)
    :param str description: a description of the world (default is None)
    """
    uid = 0

    def __init__(self, nodes, lfunc, **kwargs):
        self.uid = self.__class__.uid
        self.__class__.uid += 1
        self.name = kwargs.get('name', 'world{}'.format(self.uid))
        self.description = kwargs.get('description', None)
        self._nodes = nodes
        self.lfunc = lfunc
        self.edges = self.create_edges()
        
    @property
    def nodes(self):
        """Nodes IDs."""
        return list(range(len(self._nodes)))
    
    def create_edges(self):
        """Create edges from the nodes.
        
        The job of this method is to map node ID pairs to :class:`Edge`
        instances that describe the edge between the nodes at the given
        indices. Note that all of the :class:`Edge`\s are created within this
        method.
        
        :return: a mapping of node ID pairs to :class:`Edge` instances.
        :rtype: :class:`dict`
        """
        edges = {}
        for m in self.nodes:
            for n in self.nodes:
                a, b = self.data(m), self.data(n)
                if a != b:
                    edge = Edge(a, b, length=self.lfunc(a, b))
                    edges[m, n] = edge
        return edges
        
    def reset_pheromone(self, level=0.01):
        """Reset the amount of pheromone on every edge to some base *level*.
        
        Each time a new set of solutions is to be found, the amount of
        pheromone on every edge should be equalized to ensure un-biased initial
        conditions. 
        
        :param float level: amount of pheromone to set on each edge 
                            (default=0.01)
        """
        for edge in self.edges.values():
            edge.pheromone = level
        
    def data(self, idx, idy=None):
        """Return the node data of a single id or the edge data of two ids.

        If only *idx* is specified, return the node with the ID *idx*. If *idy*
        is also specified, return the :class:`Edge` between nodes with indices
        *idx* and *idy*.

        :param int idx: the id of the first node
        :param int idy: the id of the second node (default is None)
        :return: the node with ID *idx* or the :class:`Edge` between nodes
                  with IDs *idx* and *idy*.
        :rtype: node or :class:`Edge`
        """
        try:
            if idy is None:
                return self._nodes[idx]
            else:
                return self.edges[idx, idy]
        except IndexError:
            return None


class Edge:
    """This class represents the link between starting and ending nodes.

    In addition to *start* and *end* nodes, every :class:`Edge` has *length*
    and *pheromone* properties. *length* represents the static, *a priori*
    information, whereas *pheromone* level represents the dynamic, *a
    posteriori* information.
    
    :param Node a: the node at the start of the :class:`Edge`
    :param Node b: the node at the end of the :class:`Edge`
    :param float length: the length of the :class:`Edge` (default=1)
    :param float pheromone: the amount of pheromone on the :class:`Edge` 
                            (default=0.1)
    """
    def __init__(self, a, b, length=None, pheromone=None):
        self.start = a
        self.end = b
        self.length = 1 if length is None else length
        self.pheromone = 0.1 if pheromone is None else pheromone

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
        
