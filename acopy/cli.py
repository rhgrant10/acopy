# -*- coding: utf-8 -*-

"""Console script for acopy."""
import time
import random

import click

from . import ant
from . import solvers
from . import plugins
from . import utils


def solver_options(f):
    click.option('--seed',
                 type=str,
                 default=None,
                 help='set the random seed')(f)
    click.option('--plot',
                 default=False,
                 is_flag=True,
                 help='enable pretty graphs that show interation data (you '
                      'must have matplotlib and pandas installed)')(f)
    click.option('--darwin',
                 default=0.0,
                 help='sigma factor for variation of the alpha/beta settings '
                      'for ants between iterations')(f)
    click.option('--flip',
                 type=int,
                 default=None,
                 help='seconds between periodic inversions of the pheromone '
                      'levels on all edges, meaning the edges with the least '
                      'pheromone will have the most and vice versa')(f)
    click.option('--threshold',
                 type=float,
                 default=None,
                 help='solution value below which the solver will stop')(f)
    click.option('--reset',
                 type=int,
                 default=False,
                 help='seconds between periodic resets of the pheromone '
                      'levels on all edges')(f)
    click.option('--elite',
                 default=0.0,
                 help='how many times the best solution is re-traced')(f)
    click.option('--limit',
                 default=2000,
                 show_default=True,
                 help='maximum number of iterations to perform')(f)
    click.option('--ants',
                 type=int,
                 default=None,
                 help='number of ants to use (defaults to number of nodes)')(f)
    click.option('--top',
                 default=None,
                 help='number of ants that deposit pheromone (defaults to '
                      'all)')(f)
    click.option('--q',
                 default=1.0,
                 help='amount of pheromone each ant has')(f)
    click.option('--rho',
                 default=0.03,
                 help='rate of pheromone evaporation')(f)
    click.option('--beta',
                 default=3.0,
                 help='how much pheromone matters')(f)
    click.option('--alpha',
                 default=1.0,
                 help='how much distance matters')(f)
    return f


def run_solver(graph, alpha, beta, rho, q, limit, top, ants, seed,
               plugin_settings):
    if plugin_settings.get('plot') and not utils.is_plot_enabled():
        raise click.UsageError('you must install matplotlib and pandas to '
                               'use the --plot option')
    seed = seed or str(hash(time.time()))
    click.echo(f'SEED={seed}')
    random.seed(seed)

    colony = ant.Colony(alpha=alpha, beta=beta)
    solver = solvers.Solver(rho=rho, q=q, top=top)

    click.echo(solver)
    click.echo('Registering Printout plugin...')
    solver.add_plugin(plugins.Printout())

    click.echo('Registering Timer plugin...')
    timer = plugins.Timer()
    solver.add_plugin(timer)

    if plugin_settings.get('plot'):
        click.echo('Registering StatsRecorder plugin...')
        solver.add_plu_settingsin(plugins.StatsRecorder())
    if plugin_settings.get('darwin'):
        click.echo('Registering Darwin plugin...')
        value = plugin_settings['darwin']
        solver.add_plugin(plugins.Darwin(sigma=value))
    if plugin_settings.get('elite'):
        click.echo('Registering EliteTracer plugin...')
        value = plugin_settings['elite']
        solver.add_plugin(plugins.EliteTracer(factor=value))
    if plugin_settings.get('reset'):
        click.echo('Registering PeriodicReset plugin...')
        value = plugin_settings['reset']
        solver.add_plugin(plugins.PeriodicReset(period=value))
    if plugin_settings.get('flip'):
        click.echo('Registering PheromoneFlip plugin...')
        value = plugin_settings['flip']
        solver.add_plugin(plugins.PheromoneFlip(period=value))
    if plugin_settings.get('threshold'):
        click.echo('Registering ThresholdPlugin plugin...')
        value = plugin_settings['threshold']
        solver.add_plugin(plugins.Threshold(value))

    solver.solve(graph, colony, gen_size=ants, limit=limit)

    click.echo(timer.get_report())
    if plugin_settings.get('plot'):
        data = solver.plugins['stats-recorder'].stats
        plotter = utils.plot.Plotter(data)
        plotter.plot()


@click.group()
def main():
    if not utils.is_plot_enabled():
        click.echo(click.style('warning: plotting feature disabled',
                               fg='yellow'))


@main.command(short_help='run the demo')
@solver_options
def demo(alpha, beta, rho, q, limit, top, ants, seed, **plugin_settings):
    """Run the solver against the 33-city demo graph."""
    graph = utils.get_demo_graph()
    run_solver(graph, alpha, beta, rho, q, limit, top, ants, seed,
               plugin_settings)


@main.command(short_help='use the solver on a graph')
@solver_options
@click.argument('filepath',
                type=click.Path(dir_okay=False, readable=True))
@click.option('--format',
              default='json',
              type=click.Choice(utils.data.get_formats()),
              show_default=True,
              metavar='FORMAT',
              help='format of the file containing the graph to use; choices '
                   f'are {", ".join(utils.data.get_formats())}')
def solve(alpha, beta, rho, q, limit, top, ants, filepath, format, seed,
          **plugin_settings):
    """Use the solver on a graph in a file in one of several formats."""
    try:
        graph = utils.data.read_graph_data(filepath, format)
    except Exception:
        raise click.UsageError(f'failed to parse {filepath} as {format}')
    run_solver(graph, alpha, beta, rho, q, limit, top, ants, seed,
               plugin_settings)


if __name__ == "__main__":
    main()
