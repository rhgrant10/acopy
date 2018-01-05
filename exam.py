import math
import string
import random

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


def get_random_world(size=10, min_dist=1, max_dist=5):
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

    builder = pants.world.WorldBuilder()
    return builder.from_lookup_table(graph, symmetrical=True)


def get_simple_world():
    graph = {}
    graph['A', 'B'] = 2
    graph['B', 'C'] = 4
    graph['C', 'D'] = 6
    graph['A', 'D'] = 8
    graph['A', 'C'] = 10
    graph['B', 'D'] = 12
    builder = pants.world.WorldBuilder()
    return builder.from_lookup_table(graph, symmetrical=True)


def dist(a, b):
    (x1, y1), (x2, y2) = a, b
    return math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def get_test_world_33():
    graph = {}
    for i, start in enumerate(TEST_COORDS_33):
        a = string.printable[i]
        for j, end in enumerate(TEST_COORDS_33[i + 1:], i + 1):
            b = string.printable[j]
            graph[a, b] = dist(start, end)

    builder = pants.world.WorldBuilder()
    return builder.from_lookup_table(graph, symmetrical=True)


def get_stuff():
    world = get_random_world(size=10, min_dist=2, max_dist=10)
    # world = get_test_world_33()
    farm = pants.ant.AntFarm()
    solver = pants.solver.Solver(farm, limit=100)

    recorder = pants.plugins.StatRecorder()
    solver.add_plugin(recorder)

    tracer = pants.plugins.EliteTracer(factor=1)
    solver.add_plugin(tracer)

    periodic_reset = pants.plugins.PeriodicReset(period=50)
    solver.add_plugin(periodic_reset)

    return solver, world, recorder


def run(solver, world, limit=None):
    solver.limit = limit or solver.limit
    solution = solver.solve(world)
    print('Solution:')
    for edge in solution:
        print(edge)
    print('Distance:', solution.weight)
    return solution


def main(limit=100):
    solver, world, recorder = get_stuff()
    solution = run(solver, world, limit=limit)
    return solver, world, recorder, solution
