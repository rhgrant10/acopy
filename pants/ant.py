"""
.. module:: ant
    :platform: Linux, Unix, Windows
    :synopsis: Provides functionality for finding each solution step as well
               as representing a complete solution.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""

from .world import World
import itertools
import random
import bisect
import sys

class Ant:
    """
    A single independent finder of solutions to a :class:`World`.

    Each :class:`Ant` finds a solution to a world one move at a time.  They
    also represent the solution they find, and are capable of reporting which
    nodes and edges they visited, in what order they were visited, and the
    total length of the solution.

    Two properties govern the decisions each :class:`Ant` makes while finding
    a solution: *alpha* and *beta*. *alpha* controls the importance placed on
    pheromone while *beta* controls the importance placed on distance. In 
    general, *beta* should be greater than *alpha* for best results. Ants also
    have a uid property that can be used to identify a particular instance.

    Each :class:`Ant` *must be initialized* to a particular :class:`World`, and
    optionally may be given an initial node from which to start finding a
    solution. If a starting node is not given, one is chosen at random. Thus a
    few examples of instantiation and initialization might look like:

    .. code-block:: python

        ant = Ant()
        ant.initialize(world)

    .. code-block:: python

        ant = Ant(alpha=0.5, beta=2.25)
        ant.initialize(world, start=world.nodes[0])

    .. note::

        The examples above assume the world has already been created!

    :class:`Ant`\s may be cloned, which will not preserve the *uid* property
    while returning a shallow copy. If this behavior is not desired, simply
    use the ``copy`` or ``deepcopy`` modules as necessary.
    
    Once an :class:`Ant` has found a solution (or at any time), the solution
    may be obtained and inspected by accessing its ``tour`` property, which
    returns the nodes visited in order, or it's ``path`` property, which 
    returns the edges visited in order. Also, the total distance of the 
    solution can be accessed through its ``distance`` property.

    """
    uid = 0

    def __init__(self, alpha=1, beta=3):
        """Create a new Ant for the given world.

        :param float alpha: the relative importance of pheromone (default=1)
        :param float beta: the relative importance of distance (default=3)
        
        """
        self.uid = Ant.uid
        Ant.uid += 1
        self.world = None
        self.alpha = alpha
        self.beta = beta
        self.start = None
        self.distance = 0
        self.visited = []
        self.unvisited = []
        self.traveled = []

    def initialize(self, world, start=None):
        """Reset everything so that a new solution can be found.

        :param World world: the world to solve
        :param Node start: the starting node (default is choosen randomly)

        """
        self.world = world
        if start is None:
            self.start = random.randrange(len(self.world.nodes))
        else:
            self.start = start
        self.distance = 0
        self.visited = [self.start]
        self.unvisited = [n for n in self.world.nodes if n != self.start]
        self.traveled = []
        return self

    def clone(self):
        """Return a shallow copy with a new UID.

        :returns: a clone
        :rtype: :class:`Ant`

        """
        ant = Ant(self.alpha, self.beta)
        ant.world = self.world
        ant.start = self.start
        ant.visited = self.visited[:]
        ant.unvisited = self.unvisited[:]
        ant.traveled = self.traveled[:]
        ant.distance = self.distance
        return ant


    @property
    def node(self):
        """Node at which the :class:`Ant` currently sits."""
        try:
            return self.visited[-1]
        except IndexError:
            return None

    @property
    def tour(self):
        """Nodes visited by the :class:`Ant` in order."""
        return [self.world.data(i) for i in self.visited]

    @property
    def path(self):
        """Edges traveled by the :class:`Ant` in order."""
        return self.traveled

    def __lt__(self, other):
        """Return True if the distance is less than the other distance."""
        return self.distance < other.distance

    def can_move(self):
        """Return True if there are still unvisited nodes."""
        return len(self.traveled) != len(self.visited)

    def move(self):
        """Choose a move and make it."""
        remaining = self.remaining_moves()
        choice = self.choose_move(remaining)
        return self.make_move(choice) # returns edge

    def remaining_moves(self):
        """Return the moves that remain to be made."""
        return self.unvisited

    def choose_move(self, choices):
        """Choose a move from all possible moves."""
        if len(choices) == 0:
            return None
        if len(choices) == 1:
            return choices[0]
        weights = []
        for move in choices:
            edge = self.world.edges[self.node, move]
            weights.append(self.weigh(edge))
        total = sum(weights)
        cumdist = list(itertools.accumulate(weights)) + [total]
        return choices[bisect.bisect(cumdist, random.random() * total)]

    def make_move(self, dest):
        """Move to the *dest* node and return the edge traveled."""
        # Since self.node simply refers to self.visited[-1], which will be
        # changed before we return to calling code, store a reference now.
        ori = self.node

            
        # When dest is None, all nodes have been visited but we may not
        # have returned to the node on which we started. If we have, then
        # just do nothing and return None. Otherwise, set the dest to the
        # node on which we started and don't try to move it from unvisited
        # to visited because it was the first one to be moved.
        if dest is None:
            if self.can_move() is False:
                return None
            dest = self.start   # last move is back to the start
        else:
            self.visited.append(dest)
            self.unvisited.remove(dest)
        
        edge = self.world.edges[ori, dest]
        self.traveled.append(edge)
        self.distance += edge.length
        return edge

    def weigh(self, edge):
        """Calculate the weight of a given *edge*."""
        pre = 1 / (edge.length or 1)
        post = edge.pheromone
        return post ** self.alpha * pre ** self.beta

    
