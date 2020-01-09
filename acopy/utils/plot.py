# -*- coding: utf-8 -*-
import functools

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import os
except ImportError:
    pass


class Plotter:
    """Utility for plotting iteration data using matplotlib.

    This is meant to be used in combination with the :class:`~StatsRecorder`
    plugin which collects stats about solutions and pheromone levels on each
    iteration.

    :param dict stats: map of stats by name
    """

    def __init__(self, stats):
        self.stats = stats

    def plot(self, is_level=True):
        """Create and show the plot."""
        plt.figure()
        plt.title('Solutions (stats)')
        self.plot_solutions()

        if is_level:
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

    def save(self, save_path='.', leading='', is_level=True):
        """Create and save the plot."""

        if not os.path.isdir(save_path):
            os.mkdir(save_path)

        plt.figure()
        plt.title('Solutions (stats)')
        self.plot_solutions()
        plt.savefig(os.path.join(save_path, leading + '_solutions.png'))

        if is_level:
            plt.figure()
            plt.title('Edge Pheromone (levels)')
            self.plot_pheromone_levels(legend=False)
            plt.savefig(os.path.join(save_path, leading + '_pheromone_levels.png'))

        plt.figure()
        plt.title('Edge Pheromone (stats)')
        self.plot_edge_pheromone()
        plt.savefig(os.path.join(save_path, leading + '_pheromone_stats.png'))

        plt.figure()
        plt.title('Solutions (uniqueness)')
        self.plot_unique_solutions()
        plt.savefig(os.path.join(save_path, leading + '_uniqueness.png'))

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
