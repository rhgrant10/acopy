# -*- coding: utf-8 -*-
import itertools


def looper(limit):
    """Return an optionally endless list of indexes."""
    if limit is not None:
        return range(limit)
    return itertools.count()


def is_plot_enabled():
    if is_plot_enabled.cache is None:
        try:
            import matplotlib  # noqa: 401
            import pandas  # noqa: 401
        except ImportError:
            is_plot_enabled.cache = False
        else:
            is_plot_enabled.cache = True
    return is_plot_enabled.cache


is_plot_enabled.cache = None
