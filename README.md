Pants
=====
###### A Python3 implementation of the Ant Colony Optimization Meta-Heuristic

Overview
--------
**Pants** provides you with the ability to quickly determine how to visit a collection of interconnected nodes such that the work done is minimized. Nodes can be any arbitrary collection of data while the edges represent the amount of "work" required to travel between two nodes. Thus, **Pants** is a tool for solving traveling salesman problems.

The world is built from a list of edges. Edges are created from two nodes, and have a length that represents the amount of "work" in moving from the first node to the second node. Note that edge length need not represent the actual length of anything.  It could, for a silly, random example, be the number of dishes one must wash before moving to the next round of a dish-washing competition.

Solutions are found through an iterative process. In each iteration, several ants are allowed to find a solution that "visits" every node of the world. The amount of pheromone on each edge is updated according to its usefulness in finding shorter solutions. The ant that traveled the least distance is considered to be the local best solution. If the local solution has a shorter distance than the best from any previous iteration, it then becomes the global best solution. The elite ant(s) then deposit their pheromone along the path of the global best solution to strengthen it further, and the process repeats.

You can read more about [Ant Colony Optimization on Wikipedia](http://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms).


Installation
------------
Currently there is no installation script (i.e., `setup.py`).  Simply copy the `pants/` directory to your `python` interpreter's `dist-packages/` directory:

```bash
$ sudo cp -r pants/ /usr/lib/python3/dist-packages
```


Useage
------
Using **Pants** is simple.  The example here uses Euclidean distance between 2D nodes with `(x, y)` coordinates, but there are no real requirements for node data of any sort.

 1) Import **Pants** (along with any other packages you'll need).

```python
import pants
import math
```

 2) Create `Node`s from your data points. Although the `Node` class is available for use, any *hashable* data type (such as `tuple` or `namedtuple`) will work.  `Node`s accept any keyword arguments and turns them into attributes. Here, `data_points` is a list of `dict`s.

```python
data_points = [
    {'x': 0, 'y': 0, 'name': 'origin'},
    {'x': 1, 'y': 1, 'name': 'node one'},
    {'x': 0, 'y': 5, 'name': 'node two'},
    {'x': 3, 'y': 4, 'name': 'node three'}
]
nodes = [pants.Node(**d) for d in data_points]
```

 3) Create `Edge`s and set their `length` property to represent the work required to traverse it.  Here the work required is the Euclidean distance between the two nodes (which have all been given `x` and `y` component properties to represent their position).

```python
edges = [Edge(a, b, length=math.sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2))]
```

 4) Create a `World` from the edges. Note that edges can also be added individually after the world has been instantiated by using the `add_edge` method.

```python
world = World(edges[:-1])
world.add_edge(edges[-1])
```

 5) Create a `Solver` for the `World`.

```python
solver = Solver(world)
```

 6) Solve the `World` with the `Solver`. Two methods are provided for finding solutions: `solve()` and `solutions()`. The former returns the best solution found, whereas the latter returns each solution found if it is the best thus far.

```python
solution = solver.solve()
# or
solutions = solver.solutions()
```

  7) Inspect the solution(s).

```python
print(solution.distance)
print(solution.path)
print(solution.moves)
# or
best = float("inf")
for solution in solutions:
  assert solution.distance < best
  best = solution.distance
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

Time Elapsed              Distance                 
--------------------------------------------------
           0:00:00.121161 0.7456617142242          
           0:00:00.241535 0.6712008988126722       
           0:00:00.591824 0.6458602513913229       
           0:00:00.824825 0.636470460214415        
           0:00:01.403655 0.6228641130880773       
--------------------------------------------------
Best solution:
         2 = {"x": 34.02115, "y": -84.267249}
        15 = {"x": 34.048194, "y": -84.262126}
        12 = {"x": 34.044915, "y": -84.255772}
        22 = {"x": 34.060164, "y": -84.242514}
         3 = {"x": 34.061518, "y": -84.243566}
        28 = {"x": 34.062461, "y": -84.240155}
        24 = {"x": 34.060461, "y": -84.237402}
        26 = {"x": 34.063814, "y": -84.225499}
         4 = {"x": 34.064489, "y": -84.22506}
         9 = {"x": 34.066471, "y": -84.217717}
        23 = {"x": 34.059412, "y": -84.216757}
        20 = {"x": 34.055487, "y": -84.217882}
        19 = {"x": 34.051529, "y": -84.218865}
        17 = {"x": 34.048679, "y": -84.224917}
        18 = {"x": 34.04951, "y": -84.226327}
        14 = {"x": 34.046006, "y": -84.225258}
        13 = {"x": 34.045483, "y": -84.221723}
        16 = {"x": 34.048312, "y": -84.208885}
        21 = {"x": 34.056326, "y": -84.20058}
         1 = {"x": 34.024302, "y": -84.16382}
        31 = {"x": 34.109645, "y": -84.177031}
        27 = {"x": 34.116852, "y": -84.163971}
         6 = {"x": 34.118162, "y": -84.163304}
         5 = {"x": 34.10584, "y": -84.21667}
        10 = {"x": 34.071628, "y": -84.265784}
        30 = {"x": 34.068647, "y": -84.283569}
        29 = {"x": 34.068455, "y": -84.283782}
         7 = {"x": 34.061468, "y": -84.33483}
        25 = {"x": 34.061281, "y": -84.334798}
        11 = {"x": 34.023101, "y": -84.36298}
         0 = {"x": 34.022718, "y": -84.361903}
        32 = {"x": 34.022585, "y": -84.36215}
         8 = {"x": 34.021342, "y": -84.363437}
Solution length: 0.6228641130880773
Found at 0:00:01.403655 out of 0:00:11.397432 seconds.
$
```

Known Bugs
----------
 
None that I'm aware of currently.  Please let me know if you find otherwise!


Troubleshooting
---------------

Credits
-------
 
 * Robert Grant <rhgrant10@gmail.com>

License
-------

GPL
