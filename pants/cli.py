# -*- coding: utf-8 -*-

"""Console script for pants."""
import time
import random

import click

from . import ant
from . import solvers
from . import plugins
from . import utils


@click.group()
@click.option('--global-seed', type=int, default=None)
def main(global_seed):
    global_seed = global_seed or hash(time.time())
    print(f'SEED={global_seed}')
    random.seed(global_seed)


@main.command()
@click.option('--file', type=click.Path(dir_okay=False, readable=True),
              help='name of a file containing the graph to use')
@click.option('--alpha', default=1.0,
              help='how much important the ants give to the distance when '
                   'evaluating which edge to travel')
@click.option('--beta', default=3.0,
              help='how much imporance the ants give to the pheromone when '
                   'evaluating which edge to travel')
@click.option('--rho', default=0.03,
              help='ratio of pheromone that remains after evaporation between '
                   'iterations')
@click.option('--q', default=1.0,
              help='amount of pheromone each ant has')
@click.option('--gen-size', type=int, default=60,
              help='number of ants in each generation')
@click.option('--limit', default=2000,
              help='maximum number of iterations to perform')
@click.option('--elite', default=0.0,
              help='factor controlling how many ants will trace the global '
                   'best solution after each iteration')
@click.option('--plot/--no-plot', default=False,
              help='enable or disable the use of matplotlib to show pretty '
                   'graphs once all iterations are complete (you must have '
                   'matplotlib and pandas installed)')
@click.option('--reset', type=int, default=False,
              help='seconds between periodic resets of the pheromone levels '
                   'on all edges')
@click.option('--threshold', type=float, default=None,
              help='solution value below which the solver will stop')
@click.option('--flip', type=int, default=False,
              help='seconds between periodic flips of the pheromone levels on '
                   'all edges, meaning the edges with the least pheromone '
                   'will have the most and vice versa')
@click.option('--darwin', default=0.0,
              help='sigma factor for variation of the alpha/beta settings for '
                   'ants in each generation')
def demo(alpha, beta, rho, q, limit, gen_size, file, plot, darwin, elite, flip,
         threshold, reset):
    if file is None:
        graph = utils.get_test_world_33()
    else:
        graph = utils.read_graph_from_file(file)

    colony = ant.Colony(alpha=alpha, beta=beta)
    solver = solvers.Solver(rho=rho, q=q)

    solver.add_plugin(plugins.PrintoutPlugin())
    solver.add_plugin(plugins.TimerPlugin())

    if plot:
        solver.add_plugin(plugins.StatsRecorder())
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
    if plot:
        data = solver.plugins['stats-recorder'].stats
        plotter = utils.Plotter(data)
        plotter.plot()


if __name__ == "__main__":
    main()
