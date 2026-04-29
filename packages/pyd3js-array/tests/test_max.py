from __future__ import annotations

import json

import pytest

from pyd3js_array import max


def box(value: object) -> dict[str, object]:
    return {"value": value}


def unbox(b: dict[str, object], *_: object) -> object:
    return b["value"]


class _ObjNaN:
    def valueOf(self) -> float:
        return float("nan")


class _ObjBadValueOf:
    def valueOf(self) -> float:
        raise RuntimeError("boom")


def test_max_numbers() -> None:
    assert max([1]) == 1
    assert max([5, 1, 2, 3, 4]) == 5
    assert max([20, 3]) == 20
    assert max([3, 20]) == 20


def test_max_strings() -> None:
    assert max(["c", "a", "b"]) == "c"
    assert max(["20", "3"]) == "3"
    assert max(["3", "20"]) == "3"


def test_max_ignores_null_nan() -> None:
    o = _ObjNaN()
    assert max([float("nan"), 1, 2, 3, 4, 5]) == 5
    assert max([o, 1, 2, 3, 4, 5]) == 5
    assert max([1, 2, 3, 4, 5, float("nan")]) == 5
    assert max([1, 2, 3, 4, 5, o]) == 5
    assert max([10, None, 3, None, 5, float("nan")]) == 10
    assert max([-1, None, -3, None, -5, float("nan")]) == -1


def test_max_ignores_bad_valueof() -> None:
    bad = _ObjBadValueOf()
    assert max([bad, 2, 1]) == 2
    assert max([2, bad, 1]) == 2
    assert max([2, 1, bad]) == 2


def test_max_booleans() -> None:
    assert max([True, False, 2]) == 2


def test_max_heterogenous() -> None:
    assert max([20, "3"]) == 20
    assert max(["20", 3]) == "20"
    assert max([3, "20"]) == "20"
    assert max(["3", 20]) == 20


def test_max_empty() -> None:
    assert max([]) is None
    assert max([None]) is None
    assert max([float("nan")]) is None


def test_max_accessor() -> None:
    assert max([box(1)], unbox) == 1
    assert max([box(5), box(1), box(2), box(3), box(4)], unbox) == 5


def test_max_accessor_ignores_none_nan() -> None:
    assert max([box(2), box(None), box(1)], unbox) == 2
    assert max([box(2), box(float("nan")), box(1)], unbox) == 2


def test_max_accessor_passes_d_i_array() -> None:
    results: list[list[object]] = []
    arr = ["a", "b", "c"]

    def acc(d: object, i: int, a: list[object]) -> object:
        results.append([d, i, a])
        return d

    max(arr, acc)
    assert results == [["a", 0, arr], ["b", 1, arr], ["c", 2, arr]]


@pytest.mark.oracle
def test_max_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases: list[list[object]] = [
        [1, 2, 3],
        [20, "3"],
        [True, False, 2],
        [],
        [None, 2, None, 1],
    ]
    for data in cases:
        py = max(list(data))
        ex = f"(function(){{ return d3.max({json.dumps(data)}); }})()"
        js = oracle_eval(ex)
        assert py == js, (data, py, js)


@pytest.mark.oracle
def test_max_accessor_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [{"value": 3}, {"value": 1}, {"value": 2}]
    py = max(data, lambda d, *_: d["value"])
    ex = f"(function(){{ const a = {json.dumps(data)}; return d3.max(a, d => d.value); }})()"
    js = oracle_eval(ex)
    assert py == js, (py, js)

