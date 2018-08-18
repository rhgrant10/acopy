# -*- coding: utf-8 -*-
import sys
import itertools


def looper(limit):
    """Return an optionally endless list of indexes."""
    if limit is not None:
        return range(limit)
    return itertools.count()


def is_plot_enabled():
    """Return true if plotting is enabled.

    Plotting requires matplotlib and pandas to be installed.

    :return: indication of whether plotting is enabled
    :rtype: bool
    """
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


def positive(value):
    return max(value, sys.float_info.min)
