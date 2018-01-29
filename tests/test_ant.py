import pytest
import networkx

from pants import Ant
from pants import Solution


def test_ant_get_moves():
    graph = networkx.Graph({0: [1, 2, 3]})
    solution = Solution(graph, start=0)
    moves = set(Ant().get_moves(graph, solution))
    assert moves == {1, 2, 3}


def test_ant_get_moves_when_self_edges():
    graph = networkx.Graph({0: [0, 1, 2, 3]})
    solution = Solution(graph, start=0)
    moves = set(Ant().get_moves(graph, solution))
    assert moves == {1, 2, 3}


def test_ant_get_moves_when_no_edges():
    graph = networkx.Graph({0: []})
    solution = Solution(graph, start=0)
    moves = set(Ant().get_moves(graph, solution))
    assert not moves


def test_ant_score_move():
    ant = Ant(alpha=1, beta=1)
    score = ant.score_move({'weight': 1, 'pheromone': 1})
    assert score == 1


def test_ant_score_move_when_no_weight():
    ant = Ant(alpha=1, beta=1)
    score = ant.score_move({'pheromone': 1})
    assert score == 1


def test_ant_score_move_when_no_pheromone():
    ant = Ant(alpha=1, beta=1)
    with pytest.raises(KeyError):
        ant.score_move({'weight': 1})


# class ScoreMovesUnequalWeightsCase(unittest.TestCase):
#     def test(self):


# cases
# 1. unequal pheromone
# 2. unequal weight
