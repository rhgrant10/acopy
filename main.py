import acopy
import tsplib95
import numpy as np

from acopy.plugins import Printout, StatsRecorder, MaxMinPheromoneRestrict, InitialSolution
from acopy.utils.plot import Plotter

problem = tsplib95.load_problem('bays29.tsp')
G = problem.get_graph()

solver = acopy.Solver()
colony = acopy.Colony(evil=0.02)

printer = Printout()
recoder = StatsRecorder()
initializer = InitialSolution()

solver.add_plugins(printer, recoder, initializer)

ans = solver.solve(G, colony, limit=50, gen_size=20)

plotter = Plotter(stats=recoder.stats)
plotter.plot()
