# -*- coding: utf-8 -*-
import pytest

from acopy.solvers import State


@pytest.fixture
def create_state():

    def _create_state(*bests):
        state = State(None, None, None, None, None)
        for best in bests:
            state.best = best
        return state

    return _create_state


def test_no_best_is_not_new_record(create_state):
    state = create_state()
    assert not state.is_new_record


def test_first_best_is_new_record(create_state):
    state = create_state(8)
    assert state.is_new_record


def test_record_is_lowest_best(create_state):
    state = create_state(4, 8, 10, 7, 13, 2, 5, 4, 6)
    assert state.record == 2


def test_previous_record_is_second_lowest_best(create_state):
    state = create_state(4, 8, 10, 7, 13, 2, 5, 4, 6)
    assert state.previous_record == 4
