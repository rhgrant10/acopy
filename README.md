Pants
=====
###### A Python3 implementation of the Ant Colony Optimization Meta-Heuristic

Overview
--------
I'll flesh this readme out more later, but here's the general gist.  The world is built from a list of edges.  The Euclidean distance between every combination of coordinates is calculated and a default level of pheromone is deposited along each edge.  

Solutions are found through an iterative process.  In each iteration, several ants are allowed to independently find a solution.  The pheromone levels of all the edges are updated according to their usefulness in finding a shorter solution.  The best one is considered to be the local best solution.  If the local solution beats the best from previous iterations, it then becomes the global best solution.  The elite ants then deposit their pheromone on the best solution to strengthen it further, and the process repeats for a specified number of iterations.

##### Author's Note
I wrote this on a Saturday in my pajamas, so don't judge me! ;-) Haha.  Anyway, hope it can be of use to someone.

EDIT: Now there have been several pajama Saturdays.

How to Use
----------

### From Python3

#### Creating the `World`
Pass in a list of `Node`s to create the `World`.

```python
from pants import World, Node, Edge

coords = [(1,1), (2,1), (3,2), (1,2)]
nodes = [Node(x=x, y=y) for x, y in coords]
edges = [Edge(a, b, math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)) for a in nodes for b in nodes]
world = World(edges)
```

#### Solving a `World` with the `Solver`
Once the `World` has been created, you can use the `Solver` to find a solution (the shortest tour) expressed as a list of `Node`s.

```python
from pants import Solver
from pants import World, Node, Edge

coords = [(1,1), (2,1), (3,2), (1,2)]
nodes = [Node(x=x, y=y) for x, y in coords]
edges = [Edge(a, b, math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)) for a in nodes for b in nodes]
world = World(edges)
solver = Solver(world)
solution = solver.solve()
```

#### Working with a Solution

Solutions are returned in the form of an `Ant` instance.  Each ant is capable of reporting the path it took, the distance it traveled, and generate a list of moves it made in the form of a list of (start, end) tuples.

```python
print(solution.distance)
for node in solution.path:
	print(node)
for start, end in solution.moves:
	print("{} --> {}".format(start, end))
```

Alternatively, you can iterate over incrementally better solutions.

```python
best = float("inf")
for s in solver.solutions():
	assert s.distance < best
	best = s.distance
```

Run the Demo
------------
Included is a 33 "city" demo that can be run from the command line.  Currently it accepts a single integer command line parameter to override the default iteration limit of 100.

```bash
$ cd Pants
$ ./bin/demo 99
Solver settings:
limit=99
rho=0.8, Q=1
alpha=1, beta=3
elite=0.5

Time Elapsed             	Distance                 
--------------------------------------------------
           0:00:00.168227	0.7538978282713495       
           0:00:00.334121	0.6821868352773263       
           0:00:00.659273	0.6517291553242294       
           0:00:00.821415	0.6328124955967906       
           0:00:01.137972	0.6209300816141958       
           0:00:01.455631	0.6166905121689684       
           0:00:01.935915	0.6159294335999612       
           0:00:04.625719	0.615016281912426        
           0:00:10.015411	0.6144969853063316       
--------------------------------------------------
Best solution:
         9 = (34.048194, -84.262126)
         6 = (34.044915, -84.255772)
        17 = (34.060164, -84.242514)
        22 = (34.061518, -84.243566)
        23 = (34.062461, -84.240155)
        18 = (34.060461, -84.237402)
        20 = (34.063814, -84.225499)
        24 = (34.064489, -84.225060)
        25 = (34.066471, -84.217717)
        16 = (34.059412, -84.216757)
        14 = (34.055487, -84.217882)
        13 = (34.051529, -84.218865)
        11 = (34.048679, -84.224917)
        12 = (34.049510, -84.226327)
         8 = (34.046006, -84.225258)
         7 = (34.045483, -84.221723)
        10 = (34.048312, -84.208885)
        15 = (34.056326, -84.200580)
         5 = (34.024302, -84.163820)
        31 = (34.116852, -84.163971)
        32 = (34.118162, -84.163304)
        30 = (34.109645, -84.177031)
        29 = (34.105840, -84.216670)
        28 = (34.071628, -84.265784)
        27 = (34.068647, -84.283569)
        26 = (34.068455, -84.283782)
        21 = (34.061468, -84.334830)
        19 = (34.061281, -84.334798)
         4 = (34.023101, -84.362980)
         1 = (34.021342, -84.363437)
         2 = (34.022585, -84.362150)
         3 = (34.022718, -84.361903)
         0 = (34.021150, -84.267249)
Solution length: 0.6144969853063316
Found at 0:00:10.015411 out of 0:00:15.841174 seconds.
$
```
