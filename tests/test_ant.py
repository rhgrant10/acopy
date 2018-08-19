# -*- coding: utf-8 -*-
import pytest
import networkx

from acopy import Ant
from acopy import Solution


def test_ant_get_unvisited_nodes():
    graph = networkx.Graph({0: [1, 2, 3]})
    solution = Solution(graph, start=0)
    moves = set(Ant().get_unvisited_nodes(graph, solution))
    assert moves == {1, 2, 3}


def test_ant_get_unvisited_nodes_when_self_edges():
    graph = networkx.Graph({0: [0, 1, 2, 3]})
    solution = Solution(graph, start=0)
    moves = set(Ant().get_unvisited_nodes(graph, solution))
    assert moves == {1, 2, 3}


def test_ant_get_unvisited_nodes_when_no_edges():
    graph = networkx.Graph({0: []})
    solution = Solution(graph, start=0)
    moves = set(Ant().get_unvisited_nodes(graph, solution))
    assert not moves


def test_ant_score_edge():
    ant = Ant(alpha=1, beta=1)
    score = ant.score_edge({'weight': 1, 'pheromone': 1})
    assert score == 1


def test_ant_score_edge_when_no_weight():
    ant = Ant(alpha=1, beta=1)
    score = ant.score_edge({'pheromone': 1})
    assert score == 1


def test_ant_score_edge_when_no_pheromone():
    ant = Ant(alpha=1, beta=1)
    with pytest.raises(KeyError):
        ant.score_edge({'weight': 1})
