"""A Python3 implementation of the Ant Colony Optimization Meta-Heuristic.

**Pants** provides you with the ability to quickly determine how to
visit a collection of interconnected nodes such that the work done is
minimized. Nodes can be any arbitrary collection of data while the edges
represent the amount of "work" required to travel between two nodes.
Thus, **Pants** is a tool for solving traveling salesman problems.

The world is built from a list of nodes and a function responsible for
returning the length of the edge between any two given nodes. The length
function need not return actual length. Instead, "length" refers to that 
the amount of "work" involved in moving from the first node to the second
node - whatever that "work" may be. For a silly, random example, it could
even be the number of dishes one must wash before moving to the next 
station at a least dish-washing dish washer competition.

Solutions are found through an iterative process. In each iteration,
several ants are allowed to find a solution that "visits" every node of
the world. The amount of pheromone on each edge is updated according to
its the length of solutions in which it was used. The ant that traveled the
least distance is considered to be the local best solution. If the local
solution has a shorter distance than the best from any previous
iteration, it then becomes the global best solution. The elite ant(s)
then deposit their pheromone along the path of the global best solution
to strengthen it further, and the process repeats.

You can read more about `Ant Colony Optimization on
Wikipedia <http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms>`_.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""

from .ant import Ant 
from .world import World, Edge
from .solver import Solver
