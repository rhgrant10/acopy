# -*- coding: utf-8 -*-

"""Console script for pants."""
import re
import json
import time
import math
import string
import random
import logging
import logging.config
import collections
import datetime

import click
import networkx
from matplotlib import pyplot as plt

from . import ant
from . import solvers
from . import plugins
from . import genetic
from . import utils


logging.config.dictConfig({
    'version': 1,
    # 'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'stream': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['stream'],
            'level': 'INFO',
            'propagate': True
        },
    }
})


class PrintoutPlugin(solvers.SolverPlugin):
    def initialize(self, solver):
        super().initialize(solver)
        self.iteration = 0
        self.best_count = 0
        self.width = None

    def on_start(self, state):
        self.width = math.ceil(math.log10(state.limit)) + 2

    def on_iteration(self, state):
        report = f'{self.iteration:{self.width}d}'
        self.iteration += 1
        if state.is_new_record:
            self.best_count += 1
            end = '\n'
            report += f' {self.best_count:{self.width}d} \t{state.best}'
            if hasattr(state.ants[0], 'dna'):
                report += f' {state.ants[0].dna}'
        else:
            end = '\r'
        print(report, end=end)

    def on_finish(self, state):
        print('Done' + ' ' * self.width)


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


@click.group()
@click.option('--global-seed', type=int, default=None)
def main(global_seed):
    global_seed = global_seed or hash(time.time())
    print(f'SEED={global_seed}')
    random.seed(global_seed)


@main.command('plot')
@click.option('--logfile', type=click.Path(dir_okay=False, readable=True))
def matplotlib_output(logfile):
    parser = genetic.Parser(logfile, lambda: plt.pause(0.1))
    data = []
    plt.ion()
    for generation in parser:
        scores = [t['score'] for t in generation['trials']]
        data.append(list(sorted(scores)))
        plt.gca().clear()
        plt.plot(data)


@main.command()
@click.option('--reset', type=int, default=False)
@click.option('--threshold', type=float, default=None)
@click.option('--flip', type=int, default=False)
@click.option('--elite', default=0.0)
@click.option('--darwin', default=0.0)
@click.option('--plot/--no-plot', default=False)
@click.option('--file', type=click.Path(dir_okay=False, readable=True))
@click.option('--gen-size', type=int, default=60)
@click.option('--limit', default=2000)
@click.option('--q', default=1.0)
@click.option('--rho', default=0.03)
@click.option('--beta', default=3.0)
@click.option('--alpha', default=1.0)
def demo(alpha, beta, rho, q, limit, gen_size, file, plot, darwin, elite, flip,
         threshold, reset):
    graph = read_graph_from_file(file) if file else get_test_world_33()

    colony = ant.Colony(alpha=alpha, beta=beta)
    solver = solvers.Solver(rho=rho, q=q)

    solver.add_plugin(PrintoutPlugin())
    solver.add_plugin(plugins.TimerPlugin())

    if plot:
        solver.add_plugin(plugins.StatRecorder())
    if darwin:
        solver.add_plugin(plugins.DarwinPlugin(sigma=darwin))
    if elite:
        solver.add_plugin(plugins.EliteTracer(factor=elite))
    if reset:
        solver.add_plugin(plugins.PeriodicReset(period=reset))
    if flip:
        solver.add_plugin(plugins.PheromoneFlip(period=flip))
    if threshold:
        solver.add_plugin(plugins.ThresholdPlugin(threshold))

    print(solver)
    print(f'Using {gen_size} ants from {colony}')
    print(f'Performing {limit} iterations:')

    solver.solve(graph, colony, gen_size=gen_size, limit=limit)

    print(solver.plugins['timer'].get_report())


@main.command()
@click.option('--choice-seed', type=int, default=None)
@click.option('--evo-seed', type=int, default=None)
@click.option('--file', type=click.Path(dir_okay=False, readable=True))
@click.option('--limit', default=10)
@click.option('--population', default=10)
def genetic(population, limit, file, evo_seed, choice_seed):
    seeds = random.randint(0, 2 ** 32 - 1), random.randint(0, 2 ** 32 - 1)
    if not choice_seed:
        choice_seed = seeds[0]

    if not evo_seed:
        evo_seed = seeds[1]

    graph = utils.read_graph_from_file(file) if file else get_test_world_33()
    simulator = genetic.Simulator(graph=graph, population=population,
                                  limit=limit, seed=evo_seed,
                                  choice_seed=choice_seed)
    simulator.run_forever()


@main.command()
@click.option('--max-weight', default=50.0)
@click.option('--min-weight', default=1.0)
@click.option('--size', default=10)
@click.option('--file', type=click.Path(dir_okay=False, writable=True))
def create(file, size, min_weight, max_weight):
    graph = utils.generate_random_graph(size=size, min_weight=min_weight,
                                        max_weight=max_weight)
    data = utils.graph_as_dict(graph)
    if file:
        with open(file, 'w') as f:
            json.dump(data, f)
    else:
        logging.info(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
