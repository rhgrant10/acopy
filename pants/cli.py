# -*- coding: utf-8 -*-

"""Console script for pants."""
import json
import time
import math
import string
import random
import collections

import click
import networkx
import pants


TEST_COORDS_33 = [
    (34.021150, -84.267249), (34.021342, -84.363437), (34.022585, -84.362150),
    (34.022718, -84.361903), (34.023101, -84.362980), (34.024302, -84.163820),
    (34.044915, -84.255772), (34.045483, -84.221723), (34.046006, -84.225258),
    (34.048194, -84.262126), (34.048312, -84.208885), (34.048679, -84.224917),
    (34.049510, -84.226327), (34.051529, -84.218865), (34.055487, -84.217882),
    (34.056326, -84.200580), (34.059412, -84.216757), (34.060164, -84.242514),
    (34.060461, -84.237402), (34.061281, -84.334798), (34.063814, -84.225499),
    (34.061468, -84.334830), (34.061518, -84.243566), (34.062461, -84.240155),
    (34.064489, -84.225060), (34.066471, -84.217717), (34.068455, -84.283782),
    (34.068647, -84.283569), (34.071628, -84.265784), (34.105840, -84.216670),
    (34.109645, -84.177031), (34.116852, -84.163971), (34.118162, -84.163304),
]


def dist(a, b):
    (x1, y1), (x2, y2) = a, b
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def get_test_world_33():
    graph = collections.defaultdict(dict)
    for i, start in enumerate(TEST_COORDS_33):
        a = string.printable[i]
        for j, end in enumerate(TEST_COORDS_33[i + 1:], i + 1):
            b = string.printable[j]
            graph[a][b] = {'weight': dist(start, end)}
    return networkx.Graph(graph)


class PrintoutPlugin(pants.SolverPlugin):
    def initialize(self, solver):
        super().initialize(solver)
        self.iteration = 0
        self.best_count = 0
        self.width = None

    def on_start(self, graph, ants, gen_size, limit):
        self.width = math.ceil(math.log10(limit)) + 2

    def on_iteration(self, graph, solutions, best, is_new_best):
        report = f'{self.iteration: {self.width}d}'
        self.iteration += 1
        if is_new_best:
            self.best_count += 1
            end = '\n'
            report += (f' {self.best_count: {self.width}d} \t{best}')
        else:
            end = '\r'
        print(report, end=end)

    def on_finish(self, **kwargs):
        print('Done' + ' ' * self.width)


class TimerPlugin(pants.SolverPlugin):
    def initialize(self, solver):
        super().initialize(solver)
        self.start_time = None
        self.finsih_time = None
        self.duration = None

    def on_start(self, **kwargs):
        self.start_time = time.time()

    def on_finish(self, **kwargs):
        self.finsih_time = time.time()
        self.duration = self.finsih_time - self.start_time
        print(f'Total time: {self.duration} seconds')


def write_graph(filepath, graph):
    data = collections.defaultdict(dict)
    for (a, b), w in graph.items():
        data[a][b] = {'weight': w}
    with open(filepath, 'w') as f:
        json.dump(data, f)


def generate_random_graph(size=10, min_weight=1, max_weight=50):
    graph = networkx.complete_graph(string.printable[:size])
    for e in graph.edges:
        w = random.randint(min_weight, max_weight)
        graph.edges[e]['weight'] = {'weight': w}
    return graph


def read_graph_from_file(filepath):
    with open(filepath) as f:
        data = json.load(f)
    graph = networkx.Graph(data)
    return graph


@click.group()
def main():
    pass


@main.command()
@click.option('--file', type=click.Path(dir_okay=False, readable=True))
@click.option('--size', type=int, default=60)
@click.option('--elite', default=0.0)
@click.option('--limit', default=2000)
@click.option('--q', default=1.0)
@click.option('--rho', default=0.03)
@click.option('--beta', default=3.0)
@click.option('--alpha', default=1.0)
def demo(alpha, beta, rho, q, limit, elite, size, file):
    args = 'alpha={alpha} beta={beta} rho={rho} limit={limit} gen-size={size}'
    print(args.format(**locals()))

    colony = pants.Colony(alpha=alpha, beta=beta)
    solver = pants.Solver(rho=rho, q=q)
    graph = read_graph_from_file(file) if file else get_test_world_33()

    recorder = pants.plugins.StatRecorder()
    solver.add_plugins(recorder, PrintoutPlugin(), TimerPlugin())

    if elite:
        solver.add_plugin(pants.plugins.EliteTracer())

    solver.solve(graph, colony, gen_size=size, limit=limit)
    recorder.plot()


@main.command()
@click.option('--max-weight', default=50.0)
@click.option('--min-weight', default=1.0)
@click.option('--size', default=10)
@click.argument('filepath', type=click.Path(dir_okay=False, writable=True))
def create(filepath, size, min_weight, max_weight):
    graph = generate_random_graph(size=size, min_weight=min_weight,
                                  max_weight=max_weight)
    write_graph(filepath, graph)


if __name__ == "__main__":
    main()
