=====
Usage
=====

ACOpy works with any networkx graph. Let's use tsplib95 to create one from a TSPLIB file:

.. code-block:: python

    >>> import acopy
    >>> import tsplib95
    >>> problem = tsplib95.load_problem('bayg29.tsp')
    >>> G = problem.get_graph()

With graph in hand, the first step is to create a :class:`~Solver`. There are two ACO parameters you can set on instantiation: ``rho`` and ``q``.

.. code-block:: python

    >>> solver = acopy.Solver(rho=.03, q=1)

We also need a colony. Colonies are the source of ants. The :class:`~Colony` class let's you set the other two ACO paramters: ``alpha`` and ``beta``.

.. code-block:: python

    >>> solver = acopy.Colony(alpha=1, beta=3)

Now we can start solving! Let's do 100 iterations with a default number of ants.

.. code-block:: python

    >>> best = solver.solve(G, colony, limit=100)
