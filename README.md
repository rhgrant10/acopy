pants
=====

A Python implementation of the Ant Colony Optimization Meta-Heuristic

Overview
--------
I'll flesh this readme out more later, but here's the general gist.  The world is built from a list of x and y coordinates.  The Euclidean distance between every combination of coordinates is calculated and a default level of pheromone is deposited along each edge.  

Solutions are found through an iterative process.  In each iteration, several ants are allowed to independently find a solution.  The pheromone levels of all the edges are updated according to their usefulness in finding a shorter solution.  The best one is considered to be the local best solution.  If the local solution beats the best from previous iterations, it then becomes the global best solution.  The elite ants then deposit their pheromone on the best solution to strengthen it further, and the process repeats for a specified number of iterations.

### Author's Note
I wrote this on a Saturday in my pajamas, so don't judge me! ;-) Haha.  Anyway, Hope it can be of use to someone.

How to Use
----------

### From Python

Pass in a list of `(x,y)` coordinates to create the "world."

	coords = [(1,1), (2,1), (3,2), (1,2)]
    world = World(coords)

There are additional options that can affect the efficacy of the solver.

 * `p` - percent of pheromone that evaporates after each solution
 * `Q` - total amount of pheromone each ant will deposit along the path it finds
 * `t0` - initial amount of pheromone on each edge

`p` is clamped between `0` and `1` (inclusively), while `Q` is not bounded.  `t0` should be some positive (as in greater than zero) value.  These parameters have been given reasonable defaults, so don't fret too much about them if you're uncomfortable.  

Next, make the ants find the shortest solution.

    world.solve()

Again, there are several optional settings that can affect the solver.

 * `alpha` - basically, how much the ants consider distance
 * `beta` - basically, how much the ants pay attention to pheromone
 * `iter_count` - how many iterations the solver should perform
 * `ant_count` - how many ants participate in each iteration

`alpha` should be less than `beta` for best results.  `iter_count` defaults to 1000, although it is said that the algorithm can often requires as many as 2000. `ant_count` defaults to the number of coordinates that comprise the world.  Reducing the number of ants too much results in a lack of "cooperation" among the ants.

The solver is actually a generator function that returns the `Ant` that took the shortest path on each iteration.  One common use would be to keep the shortest ant of all iterations.

	global_best = None
    for local_best in world.solve():
    	if global_best is None or local_best.distance < global_best.distance:
    		global_best = local_best
    	
Here, `local_best` and `global_best` are instances of `Ant`.

	print global_best.distance  # 3.234516
	print global_best.path 		# [(x3, y3), (x1, y1), (x2, y2)]
	print global_best.moves 	# [((x3, y3), (x1, y1)),
								#  ((x1, y1), (x2, y2)),
								#  ((x2, y2), (x3, y3))]
	

### As a Shell Script

The program will perform a little 33 "city" demonstration using default settings.

    $ python pants.py


To-Do
-----

 [ ] Write more docstrings
 [ ] Start using argparse!
 [ ] Let user provide a path to a csv file of coordinates
 [ ] Let user decide whether solver returns local or global best
 [ ] Write unit tests
 [ ] Put test data someplace else
 [ ] Make this a module??
