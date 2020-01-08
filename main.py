import acopy
import tsplib95
import numpy as np

from acopy.plugins import Printout, StatsRecorder, MaxMinPheromoneRestrict
from acopy.utils.plot import Plotter

problem = tsplib95.load_problem('bays29.tsp')
G = problem.get_graph()

solver = acopy.Solver(top=1)
colony = acopy.Colony()

printer = Printout()
recoder = StatsRecorder()
restricter = MaxMinPheromoneRestrict(p_best=0.05)

solver.add_plugins(printer, recoder, restricter)

ans = solver.solve(G, colony, limit=50, gen_size=20)

plotter = Plotter(stats=recoder.stats)
plotter.plot()
