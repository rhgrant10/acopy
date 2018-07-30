# -*- coding: utf-8 -*-
import collections
import random
import string
import functools
import math

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError:
    pass
import networkx


def get_test_world_33():
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


def graph_as_dict(graph):
    data = collections.defaultdict(dict)
    for u, v in graph.edges:
        data[u][v] = graph.edges[u, v]
    return dict(data)


def generate_random_graph(size=10, min_weight=1, max_weight=50):
    graph = networkx.complete_graph(string.printable[:size])
    for e in graph.edges:
        w = random.randint(min_weight, max_weight)
        graph.edges[e]['weight'] = w
    return graph


def read_graph_from_file(filepath):
    with open(filepath) as f:
        data = json.load(f)
    graph = networkx.Graph(data)
    return graph


class Plotter:
    def __init__(self, stats):
        self.stats = stats

    def plot(self):
        plt.figure()
        plt.title('Solutions (stats)')
        self.plot_solutions()

        plt.figure()
        plt.title('Edge Pheromone (levels)')
        self.plot_pheromone_levels(legend=False)

        plt.figure()
        plt.title('Edge Pheromone (stats)')
        self.plot_edge_pheromone()

        plt.figure()
        plt.title('Solutions (uniqueness)')
        self.plot_unique_solutions()

        plt.show()

    def _plot(self, stat, ax=None, **kwargs):
        data = self._extract_and_process(stat)
        data.plot(ax=ax or plt.gca(), **kwargs)

    def __getattr__(self, name):
        if name.startswith('plot_'):
            __, stat = name.split('_', 1)
            return functools.partial(self._plot, stat)
        raise AttributeError(name)

    def _extract_and_process(self, stat):
        extractor = getattr(self, f'extract_{stat}', lambda: self.stats[stat])
        processor = getattr(self, f'process_{stat}', lambda d: pd.DataFrame(d))
        return processor(extractor())

    def extract_ant_distances(self):
        iterations = []
        for distances in self.stats['ant_distances']:
            if all(d is not None for d in distances):
                distances = list(sorted(distances))
            iterations.append(distances)
        return iterations
