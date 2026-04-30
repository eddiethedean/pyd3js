from __future__ import annotations

import json

import pytest

from pyd3js_array.mean import mean
from pyd3js_array.sum import sum_ as sum


def box(value: object) -> dict[str, object]:
    return {"value": value}


def unbox(b: dict[str, object], *_: object) -> object:
    return b["value"]


def test_sum_numbers() -> None:
    assert sum([1, 2, 3]) == 6
    assert sum([1.5, 2.5]) == 4.0


def test_sum_ignores_null_nan() -> None:
    assert sum([None, 1, 2]) == 3
    assert sum([float("nan"), 1, 2]) == 3


def test_sum_empty() -> None:
    assert sum([]) == 0
    assert sum([None, float("nan")]) == 0


def test_sum_accessor() -> None:
    data = [box(1), box(2), box(3)]
    assert sum(data, unbox) == 6


def test_mean_numbers() -> None:
    assert mean([1, 2, 3]) == 2
    assert mean([1.0, 2.0]) == 1.5


def test_mean_ignores_null_nan() -> None:
    assert mean([None, 1, 2]) == 1.5
    assert mean([float("nan"), 1, 2]) == 1.5


def test_mean_empty() -> None:
    assert mean([]) is None
    assert mean([None, float("nan")]) is None


@pytest.mark.oracle
def test_sum_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases: list[list[object]] = [
        [],
        [1, 2, 3],
        [None, 1, 2],
        [1, 2, float("nan")],
        ["1", "2", "3"],
    ]
    for data in cases:
        py = sum(list(data))
        ex = f"(function(){{ return d3.sum({json.dumps(data)}); }})()"
        js = oracle_eval(ex)
        assert py == js, (data, py, js)


@pytest.mark.oracle
def test_mean_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases: list[list[object]] = [
        [],
        [1, 2, 3],
        [None, 1, 2],
        [1, 2, float("nan")],
        ["1", "2", "3"],
    ]
    for data in cases:
        py = mean(list(data))
        ex = f"(function(){{ return d3.mean({json.dumps(data)}); }})()"
        js = oracle_eval(ex)
        assert py == js, (data, py, js)
