# -*- coding: utf-8 -*-
import itertools


def looper(limit):
    """Return an optionally endless list of indexes."""
    if limit is not None:
        return range(limit)
    return itertools.count()
