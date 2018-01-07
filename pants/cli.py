# -*- coding: utf-8 -*-

"""Console script for pants."""
import json
import time
import math
import string
import random
import collections

import click
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


def get_random_graph(size=10, min_dist=1, max_dist=5):
    delta_dist = max_dist - min_dist
    mode = delta_dist * .75 + min_dist

    def dist():
        return random.triangular(low=min_dist, high=max_dist, mode=mode)

    graph = {}
    for i in range(size):
        start = string.printable[i]
        for j in range(i + 1, size):
            end = string.printable[j]
            graph[start, end] = dist()

    return graph


def get_simple_world(builder):
    graph = {}
    graph['A', 'B'] = 2
    graph['B', 'C'] = 4
    graph['C', 'D'] = 6
    graph['A', 'D'] = 8
    graph['A', 'C'] = 10
    graph['B', 'D'] = 12
    return builder.from_lookup_table(graph)


def dist(a, b):
    (x1, y1), (x2, y2) = a, b
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def get_test_world_33(builder):
    graph = {}
    for i, start in enumerate(TEST_COORDS_33):
        a = string.printable[i]
        for j, end in enumerate(TEST_COORDS_33[i + 1:], i + 1):
            b = string.printable[j]
            graph[a, b] = dist(start, end)
    return builder.from_lookup_table(graph)


class Printout(pants.solver.SolverPlugin):
    def initialize(self, solver):
        self.solver = solver
        self.iteration = 0
        self.best_count = 0
        self.width = math.ceil(math.log10(self.solver.limit)) + 2

    def on_iteration(self, colony, global_best, is_new_best):
        report = f'{self.iteration: {self.width}d}'
        self.iteration += 1
        if is_new_best:
            self.best_count += 1
            end = '\n'
            solution = ''.join(global_best.nodes)
            report += (f' {self.best_count: {self.width}d} '
                       f'{solution} {global_best.weight}')
        else:
            end = '\r'
        print(report, end=end)

    def on_finish(self, colony, global_best):
        print('Done' + ' ' * self.width)


class Timer(pants.solver.SolverPlugin):
    def initialize(self, *args):
        self.start_time = None
        self.finsih_time = None
        self.duration = None

    def on_start(self, *args):
        self.start_time = time.time()

    def on_finish(self, *args):
        self.finsih_time = time.time()
        self.duration = self.finsih_time - self.start_time
        print(f'Total time: {self.duration} seconds')


def write_graph(filepath, graph):
    data = collections.defaultdict(dict)
    for (a, b), d in graph.items():
        data[a][b] = d
    with open(filepath, 'w') as f:
        json.dump(data, f)


def read_graph(filepath):
    with open(filepath) as f:
        data = json.load(f)

    graph = {}
    for a, edges in data.items():
        for b, d in edges.items():
            graph[a, b] = d
    return graph


@click.group()
def main():
    pass


@main.command()
@click.option('--file', type=click.Path(dir_okay=False, readable=True))
@click.option('--size', type=int, default=None)
@click.option('--elite', default=0.0)
@click.option('--limit', default=100)
@click.option('--q', default=1.0)
@click.option('--rho', default=0.5)
@click.option('--beta', default=3.0)
@click.option('--alpha', default=1.0)
def demo(alpha, beta, rho, q, limit, elite, size, file):
    print(alpha, beta, rho, q, limit, size)
    farm = pants.ant.SpecificAntFarm(alpha=alpha, beta=beta, q=q)
    solver = pants.solver.Solver(farm, limit=limit)

    recorder = pants.plugins.StatRecorder()
    # reset = pants.plugins.PeriodicReset()
    printout = Printout()
    timer = Timer()
    solver.add_plugins(
        recorder,
        printout,
        timer,
        # reset,  # not ready... something wrong
    )

    if elite:
        solver.add_plugin(pants.plugins.EliteTracer())

    factory = pants.world.SpecificEdgeFactory(rho=rho, symmetrical=True)
    builder = pants.world.WorldBuilder(factory=factory)

    if file:
        graph = read_graph(file)
        print(f'Using {file}')
        world = builder.from_lookup_table(graph)
    else:
        print('Creating random graph')
        world = get_test_world_33(builder)

    solver.solve(world, size=size)
    recorder.plot()


@main.command()
@click.option('--max-dist', default=50.0)
@click.option('--min-dist', default=1.0)
@click.option('--size', default=10)
@click.argument('filepath', type=click.Path(dir_okay=False, writable=True))
def create(filepath, size, min_dist, max_dist):
    graph = get_random_graph(size=size, min_dist=min_dist, max_dist=max_dist)
    write_graph(filepath, graph)


if __name__ == "__main__":
    main()
