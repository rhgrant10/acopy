# -*- coding: utf-8 -*-
import collections
import random
import string

import networkx


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