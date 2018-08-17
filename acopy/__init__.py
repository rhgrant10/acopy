"""A Python3 implementation of the Ant Colony Optimization Meta-Heuristic.

**ACOpy** provides you with the ability to quickly determine how to
visit a collection of interconnected nodes such that the cost is minimized.
Nodes can be any arbitrary collection of data while the edges represent the
amount of "work" required to travel between two nodes. Thus, **ACOpy** is a
tool for solving traveling salesman problems.

Solutions are found through an iterative process. In each iteration,
several ants are allowed to find a solution that "visits" every node of
the world. The amount of pheromone on each edge is updated according to
the length of the solutions in which it was used. The ant that traveled the
least distance is considered to be the local best solution. If the local
solution has a shorter distance than the best from any previous
iteration, it then becomes the global best solution. This process then repeats.

You can read more about `Ant Colony Optimization on
Wikipedia <http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms>`_.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""
__author__ = """Robert Grant"""
__email__ = 'rhgrant10@gmail.com'
__version__ = '0.6.0'


from .ant import Ant  # noqa: F401
from .ant import Colony  # noqa: F401
from .solvers import Solver  # noqa: F401
from .solvers import Solution  # noqa: F401
from .solvers import SolverPlugin  # noqa: F401
from . import plugins  # noqa: F401
from . import utils  # noqa: F401
