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

.. code-block:: python

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

Adding plugins to a solver can either change how the solver works or add additional functionality. Adding a plugin is easy. Let's add a plugin that times the solver:

.. code-block:: python

    >>> timer = acopy.plugins.TimerPlugin()
    >>> solver.add_plugin(timer)

Now after we solve we can get the duration and average time per iteration:

.. code-block:: python

    >>> best = solver.solve(G, colony, limit=100)
    >>> timer.duration
    4.946878910064697
    >>> timer.time_per_iter
    0.049468789100646976


Writing New Plugins
-------------------

Writing a new plugin is realtively easy. Simply subclass :class:`acopy.solvers.SolverPlugin` and provide one of the following hooks:

:on_start: called before the first iteration
:on_iteration: called upon completion of each iteration
:on_finish: called after the last iteration

Each hook takes as its only argument an instance of :class:`acopy.solvers.State` that contains information about the state of the solver.

For example, let's write a plugin that increases the number of ants each iteration.

.. code-block:: python

    class IncreasingAnts(acopy.solvers.SolverPlugin):

        def __init__(self, delta=1):
            super().__init__(delta=delta)
            self.delta = delta

        def on_iteration(self, state):
            ant = state.colony.get_ants(self.delta)
            state.ants.append(ant)

Note that you must pass the parameters you want to appear in the :func:`repr` to :func:`super` as keyword arguments:

    >>> IncreasingAnts(2)
    <IncreasingAnts(delta=2)>


Built-in Plugins
----------------

There are several plugins built into acopy. Below is a description of what they do.

Printout
~~~~~~~~

Print information about the solver as it works.

EliteTracer
~~~~~~~~~~~

Let the best ant from each iteration deposit more pheromone.

You can control how much pheromone is deposited by specifying the ``factor``. For example, to deposit an additional two times the amount of pheromone set the factor to 2:

.. code-block:: python

    >>> elite = acopy.plugins.EliteTracer(factor=2)

You can also think of this as how many additional times the best ant from each iteration deposits her pheromone.

Timer
~~~~~

Time the total duration of the solver as well as the average time per iteration.

Darwin
~~~~~~

Apply variation to the alpha and beta values on each iteration.

You can control the sigma value for the guassian distribution used to choose the next values:

.. code-block:: python

    >>> darwin = acopy.plugins.Darwin(sigma=.25)

StatsRecorder
~~~~~~~~~~~~~

Record data about the solutions and pheromone levels on each iteration.

Specifically the plugin records the amount of pheromone on every edge as well as the min, max, and average pheromone levels. It records the best, worst, average, and global best solution found for each iteration. Lastly, it tracks the number of unique soltions found for the each iteration, for all iterations, and how many unique solutions were new.


Periodic action plugins
~~~~~~~~~~~~~~~~~~~~~~~

Perform some action periodically.

Set the number of iterations that constitute a period using the ``period`` paramter:

.. code-block:: python

    >>> periodic = acopy.plugins.PeriodicActionPlugin(period=100)

By itself, the periodic action plugin does nothing but instead is designed to be subclassed. Just provide a defintion for the ``action`` method:

.. code-block:: python

    >>> import time

    >>> # plugin that periodically prints the current time
    >>> class PrintTime(acopy.plugins.PeriodicActionPlugin):
    ...     def action(self, state):
    ...         print(time.time())
    ...


There are two built-in subclasses: ``PeriodicReset`` and ``PheromoneFlip``.

PeriodicReset
#############

Periodically reset the pheromone levels.

PheromoneFlip
#############

Periodically invert the pheromone levels so that the best edges become the worst, and vice versa.



Early termination plugins
~~~~~~~~~~~~~~~~~~~~~~~~~

Terminate the solver prematurely.

Like the `PeriodicActionPlugin` this plugin does nothing by itself. You must subclass it and provide a defintion for ``should_terminate``:

    >>> import time

    >>> # plugin that stops the solver if the time is a pallendrome
    >>> class PallendromicTerminator(acopy.plugins.EarlyTerminationPlugin):
    ...     def should_terminate(self, state):
    ...         seconds = str(int(time.time()))
    ...         return list(seconds) == list(reversed(seconds))
    ...

There are two such plugins: ``Threshold`` and ``TimeLimit``.

Threshold
#########

Set a minimum threshold cost for the solver. If a solution is found that meets or dips below the threshold then the solver terminates early.

.. code-block:: python

    >>> threshold = acopy.plugins.Threshold(threshold=1719)

TimeLimit
#########

Set a time limit for the solver.

The maximum number of seconds is of course configurable. The plugin will stop the solver from iterating again if the number of seconds exceeds the value set:

.. code-block:: python

    >>> time_limit = acopy.plugins.TimeLimit(seconds=30)

Note this means that it is possible to exceed the time limit since it will not stop the solver mid-iteration.


CLI Tool
========

The CLI tool included provides a quick way to solve graphs saved as files in a variety of formats.

.. code-block:: console

    $ acopy solve --file ~/Downloads/ALL_tsp/burma14.tsp --file-format tsplib95 --limit 50
    SEED=172438059386129273
    Solver(rho=0.03, q=1.0, top=None)
    Registering plugin: <Printout()>
    Registering plugin: <Timer()>
    Registering plugin: <Darwin(sigma=3.0)>
    Using 33 ants from Colony(alpha=1.0, beta=3.0)
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
