# -*- coding: utf-8 -*-
import collections
import json
import string
import math

import tsplib95
import networkx


def get_formats():
    supported = ['json', 'tsplib95']
    for d in dir(networkx):
        if d.startswith('read_') and callable(getattr(networkx, d)):
            __, format_ = d.split('_', 1)
            supported.append(format_)
    supported.sort()
    return supported


def read_json(path):
    with open(path) as f:
        data = json.load(f)
    return networkx.Graph(data)


def read_tsplib95(path):
    problem = tsplib95.load_problem(path)
    return problem.get_graph()


def read_graph_data(path, format_):
    if format_ == 'json':
        read_format = read_json
    elif format_ == 'tsplib95':
        read_format = read_tsplib95
    else:
        read_format = getattr(networkx, f'read_{format_}')
    return read_format(path)


def get_demo_graph():
    TEST_COORDS_33 = [
        (34.021150, -84.267249), (34.021342, -84.363437),
        (34.022585, -84.362150), (34.022718, -84.361903),
        (34.023101, -84.362980), (34.024302, -84.163820),
        (34.044915, -84.255772), (34.045483, -84.221723),
        (34.046006, -84.225258), (34.048194, -84.262126),
        (34.048312, -84.208885), (34.048679, -84.224917),
        (34.049510, -84.226327), (34.051529, -84.218865),
        (34.055487, -84.217882), (34.056326, -84.200580),
        (34.059412, -84.216757), (34.060164, -84.242514),
        (34.060461, -84.237402), (34.061281, -84.334798),
        (34.063814, -84.225499), (34.061468, -84.334830),
        (34.061518, -84.243566), (34.062461, -84.240155),
        (34.064489, -84.225060), (34.066471, -84.217717),
        (34.068455, -84.283782), (34.068647, -84.283569),
        (34.071628, -84.265784), (34.105840, -84.216670),
        (34.109645, -84.177031), (34.116852, -84.163971),
        (34.118162, -84.163304),
    ]

    def dist(a, b):
        (x1, y1), (x2, y2) = a, b
        return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    graph = collections.defaultdict(dict)
    for i, start in enumerate(TEST_COORDS_33):
        a = string.printable[i]
        for j, end in enumerate(TEST_COORDS_33[i + 1:], i + 1):
            b = string.printable[j]
            graph[a][b] = {'weight': dist(start, end)}
    return networkx.Graph(graph)
