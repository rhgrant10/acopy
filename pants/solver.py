from .world import World
from .ant import Ant
import random

class Solver:
    """
    A world consisting of one or more coordinates in which ants find the
    shortest path that visits them all.

    """
    def __init__(self, world, **kwargs):
        self.world = world
        self.rho = kwargs.get('rho', 0.8)
        self.q = kwargs.get('Q', 1)
        self.t0 = kwargs.get('t0', .01)
        self.alpha = kwargs.get('alpha', 1)
        self.beta = kwargs.get('beta', 3)
        self.ant_count = kwargs.get('ant_count', 10)
        self.elite = kwargs.get('elite', .5)
        
    def solve(self, limit=None):
        """
        Find the shortest path that visits every coordinate.
        """
        # Reset the amount of pheromone on every edge to the initial default.
        for edge in self.world.edges.values():
            edge.pheromone = self.t0

        # Yield local bests.
        # TODO: Add option to return global best.
        elite_ant = None
        if limit is None:
            while True:
                # (Re-)Build the ant colony
                ants = self.round_robin_ants() if self.ant_count < 1 \
                        else self.random_ants()
                
                self.find_solutions(ants)
                self.update_scent(ants)
                best_ant = self.get_best_ant(ants)
                if elite_ant is None or best_ant < elite_ant:
                    elite_ant = best_ant.clone()
                if self.elite:
                    self.trace_elite(elite_ant)
                yield best_ant
        else:    
            for i in range(limit):
                # (Re-)Build the ant colony
                ants = self.round_robin_ants() if self.ant_count < 1 \
                        else self.random_ants()
                
                self.find_solutions(ants)
                self.update_scent(ants)
                best_ant = self.get_best_ant(ants)
                if elite_ant is None or best_ant < elite_ant:
                    elite_ant = best_ant.clone()
                if self.elite:
                    self.trace_elite(elite_ant)
                yield best_ant
    
    def round_robin_ants(self):
        n = len(self.world.coords)
        return [
            Ant(
                self.world, 
                self.alpha, 
                self.beta, 
                start=self.world.coords[i % n]
            ) for i in range(self.ant_count)
        ]
        
    def random_ants(self):
        starts = self.world.coords[:]
        ants = list()
        while self.ant_count > 0 and len(starts) > 0:
            r = random.randrange(len(starts))
            ants.append(
                Ant(self.world, self.alpha, self.beta, start=starts.pop(r))
            )
        return ants

    def find_solutions(self, ants):
        """
        Let each ant find its way.
        """
        ants_done = 0
        while ants_done < len(ants):
            ants_done = 0
            for ant in ants:
                if ant.can_move():
                    m = ant.move()
                    self.world.edges[m].pheromone *= self.rho
                else:
                    ants_done += 1

    def update_scent(self, ants):
        """
        Update the amount of pheromone on each edge.
        """
        ants = sorted(ants)[:len(ants) // 2]
        for move, edge in self.world.edges.items():
            edge.pheromone = (1 - self.rho) * edge.pheromone + \
                    sum(self.q / a.distance for a in ants if move in a.moves)
            if edge.pheromone < self.t0:
                edge.pheromone = self.t0

    def get_best_ant(self, ants):
        """
        Return the ant with the shortest path.
        """
        return sorted(ants)[0]

    def trace_elite(self, ant):
        """
        Deposit pheromone along the path of a particular ant n times.
        """
        if self.elite:
            for m in ant.moves:
                self.world.edges[m].pheromone += \
                        self.elite * self.q / ant.distance
    