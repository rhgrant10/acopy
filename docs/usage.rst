=====
Usage
=====

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

    >>> tour.weight
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
