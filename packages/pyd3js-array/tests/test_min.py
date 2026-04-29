from __future__ import annotations

import json

import pytest

from pyd3js_array import min


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


def test_min_numbers() -> None:
    assert min([1]) == 1
    assert min([5, 1, 2, 3, 4]) == 1
    assert min([20, 3]) == 3
    assert min([3, 20]) == 3


def test_min_strings() -> None:
    assert min(["c", "a", "b"]) == "a"
    assert min(["20", "3"]) == "20"
    assert min(["3", "20"]) == "20"


def test_min_ignores_null_nan() -> None:
    o = _ObjNaN()
    assert min([float("nan"), 1, 2, 3, 4, 5]) == 1
    assert min([o, 1, 2, 3, 4, 5]) == 1
    assert min([1, 2, 3, 4, 5, float("nan")]) == 1
    assert min([1, 2, 3, 4, 5, o]) == 1
    assert min([10, None, 3, None, 5, float("nan")]) == 3
    assert min([-1, None, -3, None, -5, float("nan")]) == -5


def test_min_ignores_bad_valueof() -> None:
    bad = _ObjBadValueOf()
    assert min([bad, 2, 1]) == 1
    assert min([2, bad, 1]) == 1
    assert min([2, 1, bad]) == 1


def test_min_booleans() -> None:
    assert min([True, False, 2]) is False


def test_min_heterogenous() -> None:
    assert min([20, "3"]) == "3"
    assert min(["20", 3]) == 3
    assert min([3, "20"]) == 3
    assert min(["3", 20]) == "3"


def test_min_empty() -> None:
    assert min([]) is None
    assert min([None]) is None
    assert min([float("nan")]) is None


def test_min_accessor() -> None:
    assert min([box(1)], unbox) == 1
    assert min([box(5), box(1), box(2), box(3), box(4)], unbox) == 1


def test_min_accessor_ignores_none_nan() -> None:
    assert min([box(2), box(None), box(1)], unbox) == 1
    assert min([box(2), box(float("nan")), box(1)], unbox) == 1


def test_min_accessor_passes_d_i_array() -> None:
    results: list[list[object]] = []
    arr = ["a", "b", "c"]

    def acc(d: object, i: int, a: list[object]) -> object:
        results.append([d, i, a])
        return d

    min(arr, acc)
    assert results == [["a", 0, arr], ["b", 1, arr], ["c", 2, arr]]


@pytest.mark.oracle
def test_min_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases: list[list[object]] = [
        [1, 2, 3],
        [20, "3"],
        [True, False, 2],
        [],
        [None, 2, None, 1],
    ]
    for data in cases:
        py = min(list(data))
        ex = f"(function(){{ return d3.min({json.dumps(data)}); }})()"
        js = oracle_eval(ex)
        assert py == js, (data, py, js)


@pytest.mark.oracle
def test_min_accessor_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [{"value": 3}, {"value": 1}, {"value": 2}]
    py = min(data, lambda d, *_: d["value"])
    ex = f"(function(){{ const a = {json.dumps(data)}; return d3.min(a, d => d.value); }})()"
    js = oracle_eval(ex)
    assert py == js, (py, js)
