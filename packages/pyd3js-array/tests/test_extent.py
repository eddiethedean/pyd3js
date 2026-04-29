from __future__ import annotations

import json

import pytest

from pyd3js_array import extent


def box(value: object) -> dict[str, object]:
    return {"value": value}


def unbox(b: dict[str, object], *_: object) -> object:
    return b["value"]


class _ObjNaN:
    def valueOf(self) -> float:
        return float("nan")


def test_extent_numbers() -> None:
    assert extent([1]) == (1, 1)
    assert extent([5, 1, 2, 3, 4]) == (1, 5)
    assert extent([20, 3]) == (3, 20)
    assert extent([3, 20]) == (3, 20)


def test_extent_strings() -> None:
    assert extent(["c", "a", "b"]) == ("a", "c")
    assert extent(["20", "3"]) == ("20", "3")
    assert extent(["3", "20"]) == ("20", "3")


def test_extent_ignores_null_nan() -> None:
    o = _ObjNaN()
    assert extent([float("nan"), 1, 2, 3, 4, 5]) == (1, 5)
    assert extent([o, 1, 2, 3, 4, 5]) == (1, 5)
    assert extent([1, 2, 3, 4, 5, float("nan")]) == (1, 5)
    assert extent([1, 2, 3, 4, 5, o]) == (1, 5)
    assert extent([10, None, 3, None, 5, float("nan")]) == (3, 10)
    assert extent([-1, None, -3, None, -5, float("nan")]) == (-5, -1)


def test_extent_heterogenous() -> None:
    assert extent([20, "3"]) == ("3", 20)
    assert extent(["20", 3]) == (3, "20")
    assert extent([3, "20"]) == (3, "20")
    assert extent(["3", 20]) == ("3", 20)


def test_extent_empty() -> None:
    assert extent([]) == (None, None)
    assert extent([None]) == (None, None)
    assert extent([float("nan")]) == (None, None)


@pytest.mark.oracle
def test_extent_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        [1, 2, 3],
        [20, "3"],
        [],
    ]
    for data in cases:
        py = extent(list(data))
        ex = f"(function(){{ return d3.extent({json.dumps(data)}); }})()"
        js = tuple(oracle_eval(ex))
        assert py == js, (data, py, js)


def test_extent_accessor() -> None:
    assert extent([box(1)], unbox) == (1, 1)
    assert extent([box(5), box(1), box(2), box(3), box(4)], unbox) == (1, 5)


def test_extent_accessor_passes_d_i_array() -> None:
    results: list[list[object]] = []
    arr = ["a", "b", "c"]

    def acc(d: object, i: int, a: list[object]) -> object:
        results.append([d, i, a])
        return d

    extent(arr, acc)
    assert results == [["a", 0, arr], ["b", 1, arr], ["c", 2, arr]]
