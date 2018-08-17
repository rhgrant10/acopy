# -*- coding: utf-8 -*-
import functools

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError:
    pass


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
