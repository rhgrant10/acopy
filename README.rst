=====
Pants
=====

A Python3 implementation of the Ant Colony Optimization Meta-Heuristic

--------
Overview
--------

**Pants** provides you with the ability to quickly determine how to
visit a collection of interconnected nodes such that the work done is
minimized. Nodes can be any arbitrary collection of data while the edges
represent the amount of "work" required to travel between two nodes.
Thus, **Pants** is a tool for solving traveling salesman problems.

The world is built from a list of edges. Edges are created from two
nodes, and have a length that represents the amount of "work" in moving
from the first node to the second node. Note that edge length need not
represent the actual length of anything. It could, for a silly, random
example, be the number of dishes one must wash before moving to the next
round of a dish-washing competition.

Solutions are found through an iterative process. In each iteration,
several ants are allowed to find a solution that "visits" every node of
the world. The amount of pheromone on each edge is updated according to
its usefulness in finding shorter solutions. The ant that traveled the
least distance is considered to be the local best solution. If the local
solution has a shorter distance than the best from any previous
iteration, it then becomes the global best solution. The elite ant(s)
then deposit their pheromone along the path of the global best solution
to strengthen it further, and the process repeats.

You can read more about `Ant Colony Optimization on
Wikipedia <http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms>`_.

------------
Installation
------------

Installation via ``pip``

.. code-block:: console

    $ pip3 install ACO-Pants

------
Useage
------

Using **Pants** is simple. The example here uses Euclidean distance
between 2D nodes with ``(x, y)`` coordinates, but there are no real
requirements for node data of any sort.

1) Import **Pants** (along with any other packages you'll need).

.. code-block:: python

        import pants
        import math

2) Create ``Node``\s from your data points. Although the ``Node`` class
   is available for use, any *hashable* data type (such as ``tuple`` or
   ``namedtuple``) will work. ``Node``\s accept any keyword arguments and
   turns them into attributes. Here, ``data_points`` is a list of
   ``dict``\s.

.. code-block:: python

      data_points = [
          {'x': 0, 'y': 0, 'name': 'origin'},
          {'x': 1, 'y': 1, 'name': 'node one'},
          {'x': 0, 'y': 5, 'name': 'node two'},
          {'x': 3, 'y': 4, 'name': 'node three'}
      ]
      nodes = [pants.Node(**d) for d in data_points]

3) Create ``Edge``\s and set their ``length`` property to represent the
   work required to traverse it. Here the work required is the Euclidean
   distance between the two nodes (which have all been given ``x`` and
   ``y`` component properties to represent their position).

.. code-block:: python

        edges = [Edge(a, b, length=math.sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2)) for a in nodes for b in nodes]

4) Create a ``World`` from the edges. Note that edges can also be added
   individually after the world has been instantiated by using the
   ``add_edge`` method.

.. code-block:: python

        world = pants.World(edges[:-1])
        world.add_edge(edges[-1])

5) Create a ``Solver`` for the ``World``.

.. code-block:: python

        solver = pants.Solver(world)

6) Solve the ``World`` with the ``Solver``. Two methods are provided for
   finding solutions: ``solve()`` and ``solutions()``. The former
   returns the best solution found, whereas the latter returns each
   solution found if it is the best thus far.

.. code-block:: python

        solution = solver.solve()
        # or
        solutions = solver.solutions()

7) Inspect the solution(s).

.. code-block:: python

        print(solution.distance)
        print(solution.path)
        print(solution.moves)
        # or
        best = float("inf")
        for solution in solutions:
          assert solution.distance < best
          best = solution.distance

Run the Demo
------------

Included is a 33 "city" demo that can be run from the command line.
Currently it accepts a single integer command line parameter to override
the default iteration limit of 100.

.. code-block:: console

    $ pants-demo 100
    Solver settings:
    limit=100
    rho=0.8, Q=1
    alpha=1, beta=3
    elite=0.5

    Time Elapsed                Distance                 
    --------------------------------------------------
               0:00:00.030429   0.7862956094256206       
               0:00:00.061907   0.7245780183747788       
               0:00:00.094099   0.6704966523088779       
               0:00:00.155262   0.649532279131667        
               0:00:00.425243   0.6478240330008148       
               0:00:00.486180   0.6460959831256239       
               0:00:00.998951   0.6386581061221168       
    --------------------------------------------------
    Best solution:
             0 = {"y": -84.221723, "x": 34.045483}
             1 = {"y": -84.225258, "x": 34.046006}
             4 = {"y": -84.224917, "x": 34.048679}
             8 = {"y": -84.226327, "x": 34.04951}
             9 = {"y": -84.218865, "x": 34.051529}
            14 = {"y": -84.217882, "x": 34.055487}
             5 = {"y": -84.216757, "x": 34.059412}
            12 = {"y": -84.217717, "x": 34.066471}
            20 = {"y": -84.225499, "x": 34.063814}
            30 = {"y": -84.22506, "x": 34.064489}
            19 = {"y": -84.242514, "x": 34.060164}
            29 = {"y": -84.243566, "x": 34.061518}
            10 = {"y": -84.240155, "x": 34.062461}
             6 = {"y": -84.237402, "x": 34.060461}
            28 = {"y": -84.255772, "x": 34.044915}
             2 = {"y": -84.262126, "x": 34.048194}
            27 = {"y": -84.267249, "x": 34.02115}
            22 = {"y": -84.363437, "x": 34.021342}
            25 = {"y": -84.36298, "x": 34.023101}
            23 = {"y": -84.36215, "x": 34.022585}
            24 = {"y": -84.361903, "x": 34.022718}
            21 = {"y": -84.33483, "x": 34.061468}
             7 = {"y": -84.334798, "x": 34.061281}
            16 = {"y": -84.283569, "x": 34.068647}
            15 = {"y": -84.283782, "x": 34.068455}
            13 = {"y": -84.265784, "x": 34.071628}
            11 = {"y": -84.21667, "x": 34.10584}
            17 = {"y": -84.177031, "x": 34.109645}
            31 = {"y": -84.163971, "x": 34.116852}
            18 = {"y": -84.163304, "x": 34.118162}
            26 = {"y": -84.16382, "x": 34.024302}
             3 = {"y": -84.208885, "x": 34.048312}
            32 = {"y": -84.20058, "x": 34.056326}
    Solution length: 0.6386581061221168
    Found at 0:00:00.998951 out of 0:00:02.994951 seconds.
    $

Known Bugs
----------

None that I'm aware of currently. Please let me know if you find
otherwise!

Troubleshooting
---------------

Credits
-------

-  Robert Grant rhgrant10@gmail.com

License
-------

GPL
