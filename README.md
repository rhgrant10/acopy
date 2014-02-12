pants
=====

A Python implementation of the Ant Colony Optimization Meta-Heuristic

Overview
--------
I'll flesh this readme out more later, but here's the general gist.  The world is built from a list of x and y coordinates.  The Euclidean distance between every combination of coordinates is calculated and a default level of pheromone is deposited along each edge.  

Solutions are found through an iterative process.  In each iteration, several ants are allowed to independently find a solution.  The pheromone levels of all the edges are updated according to their usefulness in finding a shorter solution.  The best one is considered to be the local best solution.  If the local solution beats the best from previous iterations, it then becomes the global best solution.  The elite ants then deposit their pheromone on the best solution to strengthen it further, and the process repeats for a specified number of iterations.

How to Use
--------
Firstly, you pass in a list of (x,y) coordinates to create the "world."

    world = World(coords)

There are additional options that can affect the efficacy of the solver.

 * p - percent of pheromone that evaporates after each solution
 * Q - total amount of pheromone each ant will deposit along the path it finds
 * t0 - initial amount of pheromone on each edge

p is clamped between 0 and 1 (inclusive), while Q is not bounded.  t0 should be some positive (as in greater than zero) value.  However, these parameters have been given reasonable defaults, so don't fret too much about them if you're uncomfortable.  Next, you will want to have the ants find a solution.

    world.solve()

Again, there are several optional settings that can affect the solver.

 * alpha - basically, how much the ants consider distance
 * beta - basically, how much the ants pay attention to pheromone
 * iter_count - how many iterations the solver should perform
 * ant_count - how many ants participate in each iteration