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

`Ant Colony Optimization`_ for the Traveling Salesman Problem.

* Free software: Apache Software License 2.0
* Documentation: https://acopy.readthedocs.io.


Features
--------

* Uses NetworkX_ for graph representation
* Solver can be customized via plugins
* Has a utility for plotting information about the solving process
* CLI tool that supports reading graphs in a variety of formats (including tsplib95_)
* Support for plotting iteration data using matplotlib and pandas

**ACOpy** was formerly called "Pants."

For now, only Python 3.6+ is supported. If there is demand I will add support for 3.4+.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Ant Colony Optimization`: http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms
.. _NetworkX: https://networkx.github.io/
.. _tsplib95: https://tsplib95.readthedocs.io/
