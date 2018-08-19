# -*- coding: utf-8 -*-
import pytest
import networkx

from acopy.solvers import Solution


@pytest.fixture
def graph():
    G = networkx.Graph()
    G.add_edge(1, 2, weight=2)
    G.add_edge(2, 3, weight=4)
    G.add_edge(3, 4, weight=1)
    G.add_edge(4, 1, weight=8)
    G.add_edge(1, 3, weight=5)
    G.add_edge(2, 4, weight=11)
    return G


@pytest.fixture
def create_solution(graph):

    def _create_solution(start, *nodes, is_closed=False):
        solution = Solution(graph, start)
        for node in nodes:
            solution.add_node(node)
        if is_closed:
            solution.close()
        return solution

    return _create_solution


@pytest.mark.parametrize('is_closed,answer', [
    (False, 2),
    (True, 2),
])
def test_solution_start(create_solution, is_closed, answer):
    solution = create_solution(2, 3, is_closed=is_closed)
    assert solution.start == answer


@pytest.mark.parametrize('is_closed,answer', [
    (False, 3),
    (True, 2),
])
def test_solution_current(create_solution, is_closed, answer):
    solution = create_solution(2, 3, is_closed=is_closed)
    assert solution.current == answer


@pytest.mark.parametrize('is_closed,answer', [
    (False, {2, 3}),
    (True, {2, 3}),
])
def test_solution_visited(create_solution, is_closed, answer):
    solution = create_solution(2, 3, is_closed=is_closed)
    assert solution.visited == answer


@pytest.mark.parametrize('is_closed,answer', [
    (False, [2, 3]),
    (True, [2, 3]),
])
def test_solution_nodes(create_solution, is_closed, answer):
    solution = create_solution(2, 3, is_closed=is_closed)
    assert solution.nodes == answer


@pytest.mark.parametrize('is_closed,answer', [
    (False, [(2, 3)]),
    (True, [(2, 3), (3, 2)]),
])
def test_solution_path(create_solution, is_closed, answer):
    solution = create_solution(2, 3, is_closed=is_closed)
    assert solution.path == answer


@pytest.mark.parametrize('is_closed,answer', [
    (False, 4),
    (True, 8),
])
def test_solution_cost(create_solution, is_closed, answer):
    solution = create_solution(2, 3, is_closed=is_closed)
    assert solution.cost == answer
