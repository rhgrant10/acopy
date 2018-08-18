=====
Usage
=====

Quickstart
==========

To use ACOpy in a project, you simply use it to create a :class:`~Solver` and a :class:`~Colony`:

.. code-block:: python

    >>> import acopy
    >>> solver = acopy.Solver(rho=.03, q=1)
    >>> colony = acopy.Colony(alpha=1, beta=3)

We can use the solver and the colony to solve any weighted networkx graph. Let's use :func:`tsplib95.utils.load_problem` to read a TSPLIB file into a :class:`networkx.Graph`:

.. code-block:: python

    >>> import tsplib95
    >>> problem = tsplib95.load_problem('bayg29.tsp')
    >>> G = problem.get_graph()

Solving is easy. Let's do 100 iterations with a default number of ants:

.. code-block:: python

    >>> tour = solver.solve(G, colony, limit=100)

How good was the best tour found? Let's look:

.. code-block:: python

    >>> tour.cost
    1719

You can list the solution tour in terms of the nodes or edges:

    >>> tour.nodes
    [19,
     25,
     7,
    ...
    >>> tour.path
    [(19, 25),
    (25, 7),
    (7, 23),
    ...


Solver Plugins
==============

Here's how you use them.

Available Plugins
-----------------

One
~~~

Two
~~~

Writing New Plugins
-------------------

Here's how.


CLI Tool
========

The CLI tool included provides a quick way to solve graphs saved as files in a variety of formats.

.. code-block:: console

    $ acopy solve --file ~/Downloads/ALL_tsp/burma14.tsp --file-format tsplib95 --limit 50
    SEED=172438059386129273
    Solver(rho=0.03, q=1.0, top=2)
    Registering Printout plugin...
    Registering Timer plugin...
    Using 14 ants from Colony(alpha=1.0, beta=3.0)
    Performing 50 iterations:
    Iteration   Cost    Solution
            0   42      1 14 13 12 11  9 10  8  7  6  5  4  3  2
            2   38      1 13 11  9 10  2  8  7  6  5  4  3 12 14
            3   34      1 11  9 10  2  8  7  6  5  4  3 14 12 13
            4   33      1 11  9 10  2  8 13  7  6  5  4 12  3 14
           28   32      1 11  9 10 14  3  4 12  6  5  7 13  8  2
           29   31      1 11  9 10  2  8 13  7  5  6 12  4  3 14
    Done
    Total time: 0.2856738567352295 seconds
    Avg iteration time: 0.00571347713470459 seconds
