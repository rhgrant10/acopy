pants
=====

A Python3 implementation of the Ant Colony Optimization Meta-Heuristic

Foreward
--------
Please note that this readme document may be quite out of sync with the actual code.  Sometimes I'll update the code before the readme and sometimes I'll do it the other way.  The code is going through some drastic changes at the moment, so please bear with me!

Overview
--------
I'll flesh this readme out more later, but here's the general gist.  The world is built from a list of x and y coordinates.  The Euclidean distance between every combination of coordinates is calculated and a default level of pheromone is deposited along each edge.  

Solutions are found through an iterative process.  In each iteration, several ants are allowed to independently find a solution.  The pheromone levels of all the edges are updated according to their usefulness in finding a shorter solution.  The best one is considered to be the local best solution.  If the local solution beats the best from previous iterations, it then becomes the global best solution.  The elite ants then deposit their pheromone on the best solution to strengthen it further, and the process repeats for a specified number of iterations.

##### Author's Note
I wrote this on a Saturday in my pajamas, so don't judge me! ;-) Haha.  Anyway, hope it can be of use to someone.

EDIT: Now there have been several pajama Saturdays.

How to Use
----------

### From Python3

Pass in a list of `(x,y)` coordinates to create the World.

```python
from pants.world import World

coords = [(1,1), (2,1), (3,2), (1,2)]
world = World(coords)
```

By default, the list of coordinates is used to create a complete and symmetrical set of edges from every coordinate to every other coordinate using Euclidean distances.  Alternatively, you can also pass in a dictionary of edges.  In that case, no edges are automatically created for you.  For example:

```python
from pants.world import World, Edge

coords = [(1,1), (2,1), (3,2), (1,2)]
edges = {
	(coords[0], coords[1]): Edge(coords[0], coords[1], dist=5),
	(coords[1], coords[0]): Edge(coords[1], coords[0], dist=5),
	(coords[1], coords[2]): Edge(coords[1], coords[2], dist=2000),
}
world = World(coords, edges)

print(world.distance(coords[2], coords[3]))	# -1 since no such edge exists
```

Note that edges are not symmetrtical by default!

Once the World has been created, we can use the solver to find a solution (the shortest tour) expressed as a list of coordinates.

```python
from pants.solver import Solver
from pants.world import World

coords = [(1,1), (2,1), (3,2), (1,2)]
world = World(coords)
solver = Solver(world)
solution = solver.solve()
```

Note that solutions are returned in the form of an Ant instance.  Each ant is capable of reporting the path it took, the distance it traveled, and generate a list of moves it made in the form of a list of (start, end) tuples.

```python
print(solution.distance)
for coord in solution.path:
	print(coord)
for move in solution.moves:
	print("{} --> {}".format(move[0], move[1]))
```

Alternatively, you can iterate over incrementally better solutions.

```python
best = float("inf")
for s in solver.solutions():
	assert s.distance < best
	best = s.distance
```