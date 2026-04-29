from __future__ import annotations

import json
import math

import pytest

from pyd3js_array.nice import nice
from pyd3js_array.tick_increment import tickIncrement
from pyd3js_array.tick_step import tickStep
from pyd3js_array.ticks import _tick_round, ticks


def test_tick_increment_examples() -> None:
    assert tickIncrement(0, 1, 5) == -5
    assert tickIncrement(0, 10, 5) == 2
    assert tickIncrement(0, 1, 0) is None
    assert math.isnan(tickIncrement(10, 0, 5) or float("nan"))
    assert tickIncrement(float("inf"), 1, 5) is None
    assert tickIncrement(0, 0, 5) == 0.0
    assert tickIncrement(0, 800, 10) == 100  # factor=10 branch
    assert tickIncrement(0, 100, 3) == 50  # factor=5 branch


def test_tick_step_examples() -> None:
    assert tickStep(0, 1, 5) == 0.2
    assert tickStep(0, 10, 5) == 2
    assert tickStep(10, 0, 5) == -2
    assert tickStep(0, 1, 0) is None
    assert tickStep(0, 0, 5) == 0.0
    assert tickStep(float("nan"), 1, 5) is None


def test_ticks_examples() -> None:
    assert ticks(0, 1, 5) == [0, 0.2, 0.4, 0.6, 0.8, 1]
    assert ticks(0, 10, 5) == [0, 2, 4, 6, 8, 10]
    assert ticks(10, 0, 5) == [10, 8, 6, 4, 2, 0]
    assert ticks(0, 1, 0) == []
    assert ticks(0, 0, 5) == [0.0]
    assert ticks(float("inf"), 1, 5) == []


def test_nice_examples() -> None:
    assert nice(0.2, 9.6, 5) == (0.0, 10.0)
    assert nice(9.6, 0.2, 5) == (9.6, 0.2)
    out = nice(float("nan"), 1, 5)
    assert math.isnan(out[0]) and out[1] == 1.0
    assert nice(0, 1, 0) == (0.0, 1.0)
    assert nice(0, float("inf"), 5) == (0.0, float("inf"))


def test_tick_round_guard_paths() -> None:
    assert _tick_round(1.234, 0.0) == 1.234
    assert _tick_round(float("inf"), 0.1) == float("inf")
    assert _tick_round(1.234, float("inf")) == 1.234


@pytest.mark.oracle
def test_ticks_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        (0, 1, 5),
        (0, 10, 5),
        (10, 0, 5),
        (0, 1, 0),
        (-1, 3, 4),
        (2.2, 9.7, 5),
    ]
    for start, stop, count in cases:
        py = ticks(start, stop, count)
        ex = f"(function(){{ return d3.ticks({json.dumps(start)}, {json.dumps(stop)}, {json.dumps(count)}); }})()"
        js = oracle_eval(ex)
        assert py == js, (start, stop, count, py, js)


@pytest.mark.oracle
def test_tick_step_increment_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        (0, 1, 5),
        (0, 10, 5),
        (10, 0, 5),
        (0, 1, 0),
        (-1, 3, 4),
        (2.2, 9.7, 5),
    ]
    for start, stop, count in cases:
        py_inc = tickIncrement(start, stop, count)
        py_step = tickStep(start, stop, count)

        ex_inc = f"(function(){{ return d3.tickIncrement({json.dumps(start)}, {json.dumps(stop)}, {json.dumps(count)}); }})()"
        ex_step = f"(function(){{ return d3.tickStep({json.dumps(start)}, {json.dumps(stop)}, {json.dumps(count)}); }})()"
        js_inc = oracle_eval(ex_inc)
        js_step = oracle_eval(ex_step)

        if isinstance(py_inc, float) and math.isnan(py_inc):
            assert isinstance(js_inc, float) and math.isnan(js_inc)
        else:
            assert py_inc == js_inc, (start, stop, count, py_inc, js_inc)

        assert py_step == js_step, (start, stop, count, py_step, js_step)


@pytest.mark.oracle
def test_nice_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        (0.2, 9.6, 5),
        (9.6, 0.2, 5),
        (0, 1, 0),
        (0, 1, 5),
    ]
    for start, stop, count in cases:
        py = list(nice(start, stop, count))
        ex = f"(function(){{ return d3.nice({json.dumps(start)}, {json.dumps(stop)}, {json.dumps(count)}); }})()"
        js = oracle_eval(ex)
        assert py == js, (start, stop, count, py, js)

