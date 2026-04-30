from __future__ import annotations

import json

import pytest

from pyd3js_array.greatest import greatest
from pyd3js_array.greatest_index import greatestIndex
from pyd3js_array.least import least
from pyd3js_array.least_index import leastIndex


def test_least_greatest_basic() -> None:
    assert least([3, 1, 2]) == 1
    assert greatest([3, 1, 2]) == 3


def test_least_greatest_ignores_none_nan() -> None:
    assert least([None, 3, 1, 2]) == 1
    assert greatest([None, 3, 1, 2]) == 3
    assert least([float("nan"), 3, 1, 2]) == 1


def test_least_greatest_empty() -> None:
    assert least([]) is None
    assert greatest([]) is None


def test_least_greatest_compare() -> None:
    # Reverse ordering via comparator.
    assert least([3, 1, 2], lambda a, b: b - a) == 3
    assert greatest([3, 1, 2], lambda a, b: b - a) == 1


def test_least_greatest_index_basic() -> None:
    assert leastIndex([3, 1, 2]) == 1
    assert greatestIndex([3, 1, 2]) == 0


def test_least_greatest_index_ignores_none() -> None:
    assert leastIndex([None, 3, 1, 2]) == 2


def test_least_greatest_index_empty() -> None:
    assert leastIndex([]) == -1
    assert greatestIndex([]) == -1


@pytest.mark.oracle
def test_least_greatest_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases: list[list[object]] = [
        [3, 1, 2],
        [None, 3, 1, 2],
        [],
    ]
    for data in cases:
        py_least = least(list(data))
        py_greatest = greatest(list(data))
        ex_least = f"(function(){{ return d3.least({json.dumps(data)}); }})()"
        ex_greatest = f"(function(){{ return d3.greatest({json.dumps(data)}); }})()"
        js_least = oracle_eval(ex_least)
        js_greatest = oracle_eval(ex_greatest)
        assert py_least == js_least, (data, py_least, js_least)
        assert py_greatest == js_greatest, (data, py_greatest, js_greatest)


@pytest.mark.oracle
def test_least_greatest_index_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases: list[list[object]] = [
        [3, 1, 2],
        [None, 3, 1, 2],
        [],
    ]
    for data in cases:
        py_least_i = leastIndex(list(data))
        py_greatest_i = greatestIndex(list(data))
        ex_least = f"(function(){{ return d3.leastIndex({json.dumps(data)}); }})()"
        ex_greatest = (
            f"(function(){{ return d3.greatestIndex({json.dumps(data)}); }})()"
        )
        js_least_i = oracle_eval(ex_least)
        js_greatest_i = oracle_eval(ex_greatest)
        assert py_least_i == js_least_i, (data, py_least_i, js_least_i)
        assert py_greatest_i == js_greatest_i, (data, py_greatest_i, js_greatest_i)


@pytest.mark.oracle
def test_least_greatest_compare_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [3, 1, 2]
    py_least = least(list(data), lambda a, b: b - a)
    py_greatest = greatest(list(data), lambda a, b: b - a)
    py_least_i = leastIndex(list(data), lambda a, b: b - a)
    py_greatest_i = greatestIndex(list(data), lambda a, b: b - a)

    ex_least = (
        f"(function(){{ return d3.least({json.dumps(data)}, (a,b) => b - a); }})()"
    )
    ex_greatest = (
        f"(function(){{ return d3.greatest({json.dumps(data)}, (a,b) => b - a); }})()"
    )
    ex_least_i = (
        f"(function(){{ return d3.leastIndex({json.dumps(data)}, (a,b) => b - a); }})()"
    )
    ex_greatest_i = f"(function(){{ return d3.greatestIndex({json.dumps(data)}, (a,b) => b - a); }})()"

    assert py_least == oracle_eval(ex_least)
    assert py_greatest == oracle_eval(ex_greatest)
    assert py_least_i == oracle_eval(ex_least_i)
    assert py_greatest_i == oracle_eval(ex_greatest_i)
