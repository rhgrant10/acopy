=====
ACOpy
=====


.. image:: https://img.shields.io/pypi/v/acopy.svg
        :target: https://pypi.python.org/pypi/acopy

.. image:: https://img.shields.io/travis/rhgrant10/acopy.svg
        :target: https://travis-ci.org/rhgrant10/acopy

.. image:: https://readthedocs.org/projects/acopy/badge/?version=latest
        :target: https://acopy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Ant Colony Optimization for the Traveling Salesman Problem.

**ACOpy** implements the Ant Colony Optimization Meta-Heuristic. Solutions are found
through an iterative process. In each iteration, several ants find a solution that
visits every city by considering not just the distance involved but also the amount
of pheromone along each edge. At the end of each iteration, the ants deposit
pheromone along the edges of the solution they found in inverse proportion to the
total distance. In this way, the ants remember which edges are useful and which are
not. You can read more about
`Ant Colony Optimization on Wikipedia <http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms>`_.

**ACOpy** was formerly called "Pants."

* Free software: Apache Software License 2.0
* Documentation: https://acopy.readthedocs.io.


Features
--------

* Uses NetworkX_ for graph representation
* Solver can be customized via plugins
* Has a utility for plotting information about the solving process
* CLI tool that supports reading graphs in a variety of formats (including TSPLIB)

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _NetworkX: https://networkx.github.io/