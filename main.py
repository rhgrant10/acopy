import acopy
import tsplib95
import numpy as np
import os

from acopy.plugins import StatsRecorder, MaxMinPheromoneRestrict, InitialSolution
from acopy.utils.plot import Plotter

tsps = ['bays29.tsp', 'eil76.tsp']

# images

for tsp in tsps:
    tsp_file = os.path.join('tsp_model', tsp)
    problem = tsplib95.load_problem(tsp_file)
    G = problem.get_graph()

    solver = acopy.Solver(rho=0.08, q=1)
    colony = acopy.Colony(alpha=1, beta=3)

    recorder = StatsRecorder()

    solver.add_plugins(recorder)
    solver.solve(G, colony, limit=50)

    plotter = Plotter(recorder.stats)
    plotter.save(save_path='images', leading='as' + tsp)

    solver = acopy.Solver(rho=0.08, q=1, top=1)
    colony = acopy.Colony(alpha=1, beta=3)

    recorder = StatsRecorder()
    restricter = MaxMinPheromoneRestrict(p_best=0.05, save_path='images', leading='mmas' + tsp)

    solver.add_plugins(recorder, restricter)
    solver.solve(G, colony, limit=50)

    plotter = Plotter(recorder.stats)
    plotter.save(save_path='images', leading='mmas' + tsp)
