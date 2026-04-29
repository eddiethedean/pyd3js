from __future__ import annotations

import math

import pytest

from pyd3js_array import range as d3range


def test_range_stop() -> None:
    assert d3range(5) == [0, 1, 2, 3, 4]
    assert d3range(2.01) == [0, 1, 2]
    assert d3range(1) == [0]
    assert d3range(0.5) == [0]


def test_range_stop_nonpositive() -> None:
    assert d3range(0) == []
    assert d3range(-0.5) == []
    assert d3range(-1) == []


def test_range_stop_nan() -> None:
    assert d3range(float("nan")) == []
    assert d3range() == []


def test_range_start_stop() -> None:
    assert d3range(0, 5) == [0, 1, 2, 3, 4]
    assert d3range(2, 5) == [2, 3, 4]
    assert d3range(2.5, 5) == [2.5, 3.5, 4.5]
    assert d3range(-1, 3) == [-1, 0, 1, 2]
    assert d3range(1, 1) == []
    assert d3range(2, 1) == []


def test_range_negative_step() -> None:
    assert d3range(5, 0, -1) == [5, 4, 3, 2, 1]
    assert d3range(5, 0, -2) == [5, 3, 1]
    assert d3range(5, 2, -2) == [5, 3]
    assert d3range(3, -1, -2) == [3, 1]


def test_range_step_zero() -> None:
    assert d3range(0, 5, 0) == []
    assert d3range(0, 5, float("nan")) == []
    assert d3range(0, 5, float("inf")) == []
    assert d3range(0, float("inf"), 1) == []


@pytest.mark.oracle
def test_range_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        ("d3.range(5)", d3range(5)),
        ("d3.range(2.01)", d3range(2.01)),
        ("d3.range(0)", d3range(0)),
        ("d3.range(0.5)", d3range(0.5)),
        ("d3.range(-1)", d3range(-1)),
        ("d3.range(NaN)", d3range(float("nan"))),
        ("d3.range(2, 5)", d3range(2, 5)),
        ("d3.range(1, 1)", d3range(1, 1)),
        ("d3.range(2, 1)", d3range(2, 1)),
        ("d3.range(2.5, 5)", d3range(2.5, 5)),
        ("d3.range(-1, 3)", d3range(-1, 3)),
        ("d3.range(5, 0, -1)", d3range(5, 0, -1)),
        ("d3.range(5, 0, -2)", d3range(5, 0, -2)),
        ("d3.range(5, 2, -2)", d3range(5, 2, -2)),
        ("d3.range(0, 5, 0)", d3range(0, 5, 0)),
        ("d3.range(0, 5, NaN)", d3range(0, 5, float("nan"))),
        ("d3.range(0, 5, Infinity)", d3range(0, 5, float("inf"))),
    ]
    for js_expr, py in cases:
        ex = f"(function(){{ return {js_expr}; }})()"
        js = oracle_eval(ex)
        assert py == js, (js_expr, py, js)
