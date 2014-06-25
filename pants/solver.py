"""
.. module:: solver
    :platform: Linux, Unix, Windows
    :synopsis: Provides functionality for finding a complete solution to a 
               world.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""

import random
from copy import copy

from .world import World
from .ant import Ant

class Solver:
    """This class contains the functionality for finding one or more solutions
    for a given :class:`World`.
    """
    def __init__(self, **kwargs):
        """Create a new :class:`Solver` with the given parameters.

        :param float alpha: relative importance of pheromone (default=1)
        :param float beta: relative importance of distance (default=3)
        :param float rho: percent evaporation of pheromone (0..1, default=0.8)
        :param float q: total pheromone deposited by each :class:`Ant` after
                        each interation is complete (>0, default=1)
        :param float t0: inital pheromone level along each :class:`Edge` of the
                         :class:`World` (>0, default=0.01)
        :param int limit: number of iterations to perform (default=100)
        :param float ant_count: how many :class:`Ants` will be used 
                                (default=10)
        :param float elite: multiplier of the pheromone deposited by the elite
                            :class:`Ant` (default=0.5)
        """
        self.alpha = kwargs.get('alpha', 1)
        self.beta = kwargs.get('beta', 3)
        self.rho = kwargs.get('rho', 0.8)
        self.q = kwargs.get('Q', 1)
        self.t0 = kwargs.get('t0', .01)
        self.limit = kwargs.get('limit', 100)
        self.ant_count = kwargs.get('ant_count', 10)
        self.elite = kwargs.get('elite', .5)
        
    def solve(self, world):
        """Return the single shortest path found through the given *world*.

        :param World world: the :class:`World` to solve
        
        :returns: the single best solution found
        :rtype: :class:`Ant`
        """
        world.reset_pheromone(self.t0)
        global_best = None
        for i in range(self.limit):
            # (Re-)Build the ant colony
            ants = self.round_robin_ants(world) if self.ant_count < 1 \
                    else self.random_ants(world)
            
            self.find_solutions(ants)
            self.global_update(ants)
            local_best = sorted(ants)[0]
            if global_best is None or local_best < global_best:
                global_best = copy(local_best)
            self.trace_elite(global_best)
        return global_best
    
    def solutions(self, world):
        """Return successively shorter paths through the given *world*.

        Unlike :meth:`solve`, this method returns one solution for each 
        improvement of the best solution found thus far. 

        :param World world: the :class:`World` to solve
        
        :returns: successively shorter solutions as :class:`Ant`s
        :rtype: list
        """
        world.reset_pheromone(self.t0)
        global_best = None
        for i in range(self.limit):
            # (Re-)Build the ant colony
            ants = self.round_robin_ants(world) if self.ant_count < 1 \
                    else self.random_ants(world)
            self.find_solutions(ants)
            self.global_update(ants)
            local_best = sorted(ants)[0]
            if global_best is None or local_best < global_best:
                global_best = copy(local_best)
                yield global_best
            self.trace_elite(global_best)
    
    def round_robin_ants(self, world):
        """Returns a list of :class:`Ant`s distributed to the nodes of the 
        world in a round-robin fashion.

        Note that this does not ensure at least one :class:`Ant` begins at each
        node unless there are exactly as many :class:`Ant`s as there are nodes.
        However, if *ant_count* is ``0`` then *ant_count* is set to the number
        of nodes in the :class:`World` and this method is used to create the
        :class:`Ant`s before solving.

        :param World world: the :class:`World` in which to create the ants.
        
        :returns: the :class:`Ant`s initialized to nodes in the :class:`World`
        :rtype: list
        """
        starts = world.nodes
        n = len(starts)
        return [
            Ant(self.alpha, self.beta).initialize(
                world, start=starts[i % n])
            for i in range(self.ant_count)
        ]
        
    def random_ants(self, world, even=False):
        """Returns a list of :class:`Ant`s distributed to the nodes of the 
        world in a random fashion.

        Note that this does not ensure at least one :class:`Ant` begins at each
        node unless there are exactly as many :class:`Ant`s as there are nodes.
        This method is used to create the :class:`Ant`s before solving if 
        *ant_count* is **not** ``0``.

        :param World world: the :class:`World` in which to create the ants.
        :param bool even: ``True`` if random should avoid choosing the same
                          starting node multiple times. 

        :returns: the :class:`Ant`s initialized to :class:`Node`s in the 
                  :class:`World`
        :rtype: list
        """
        ants = []
        starts = world.nodes
        n = len(starts)
        if even:
            # Since the caller wants an even distribution, use a round-robin 
            # method until the number of ants left to create is less than the
            # number of nodes.
            if self.ant_count > n:
                for i in range(self.ant_count // n):
                    ants.extend([
                        Ant(self.alpha,self.beta).initialize(
                            world, start=starts[j])
                        for j in range(n)
                    ])
            # Now (without choosing the same node twice) choose the reamining
            # starts randomly.
            ants.extend([
                Ant(self.alpha, self.beta).initialize(
                    world, start=starts.pop(random.randrange(n - i)))
                for i in range(self.ant_count % n)
            ])
        else:
            # Just pick random nodes.
            ants.extend([
                Ant(self.alpha, self.beta).initialize(
                    world, start=starts[random.randrange(n)]) 
                for i in range(self.ant_count)
            ])
        return ants

    def find_solutions(self, ants):
        """Let each ant find its own solution.

        Makes each ant move until every ant can no longer move.

        TODO: Make the local pheromone update optional and configurable.

        :param list ants: the ants to use for solving
        """
        # This loop occurs exactly as many times as there are ants times nodes,
        # but that is only because every ant must visit every node. It may be
        # more efficient to convert it to a counting loop... but what 
        # flexibility would we loose in terms of extending the solver class?
        ants_done = 0
        while ants_done < len(ants):
            ants_done = 0
            for ant in ants:
                if ant.can_move():
                    edge = ant.move()
                    self.local_update(edge)
                else:
                    ants_done += 1

    def local_update(self, edge):
        """Evaporate some of the pheromone on the given *edge*.

        This method will never let the pheromone on an edge decrease to less
        than its inital level.
        """
        edge.pheromone = max(self.t0, edge.pheromone * self.rho)

    def global_update(self, ants):
        """Update the amount of pheromone on each edge according to the fitness
        of solutions that use it.

        This accomplishes the global update performed at the end of each
        solving iteration. This method will never let the pheromone on an edge
        decrease to less than its inital level.

        :param list ants: the ants to use for solving
        """
        ants = sorted(ants)[:len(ants) // 2]
        for a in ants:
            p = self.q / a.distance
            for edge in a.path:
                edge.pheromone = max(
                    self.t0,
                    (1 - self.rho) * edge.pheromone + p)

    def trace_elite(self, ant):
        """Deposit pheromone along the path of a particular ant.

        This method is used to deposit the pheromone of the elite :class:`Ant`
        at the end of each iteration. Because this method only increases the 
        pheromone on edges, this method will never let the pheromone on an edge
        decrease to less than its inital level.

        :param Ant ant: the elite :class:`Ant`
        """
        if self.elite:
            p = self.elite * self.q / ant.distance
            for edge in ant.path:
                edge.pheromone += p
    
