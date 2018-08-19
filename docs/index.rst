Welcome to ACOpy's documentation!
======================================

This project implements the `Ant Colony Optimization Meta-Heuristic`_. Solutions are
found through an iterative process. In each iteration, several ants find a solution
that visits every city by considering not just the distance involved but also the
amount of pheromone along each edge. At the end of each iteration, the ants deposit
pheromone along the edges of the solution they found in inverse proportion to the
total distance. In this way, the ants remember which edges are useful and which are
not.

.. _`Ant Colony Optimization Meta-Heuristic`: http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   api
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
