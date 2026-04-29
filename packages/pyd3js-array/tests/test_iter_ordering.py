from __future__ import annotations

from pyd3js_array._iter import first_observed, iter_observed, iter_observed_numbers
from pyd3js_array._ordering import default_compare
from pyd3js_array.greatest_index import greatestIndex
from pyd3js_array.least_index import leastIndex


def test_default_compare_equal() -> None:
    assert default_compare(1, 1) == 0
    assert default_compare("a", "a") == 0


def test_iter_observed_with_accessor() -> None:
    data = [{"v": None}, {"v": 2}, {"v": 1}]
    out = list(iter_observed(data, lambda d, *_: d["v"]))
    assert out == [2, 1]


def test_iter_observed_accessor_returns_none() -> None:
    data = [{"v": None}]
    out = list(iter_observed(data, lambda d, *_: d["v"]))
    assert out == []


def test_iter_observed_accessor_filters_nondefinite() -> None:
    data = [{"v": float("nan")}, {"v": 1}]
    out = list(iter_observed(data, lambda d, *_: d["v"]))
    assert out == [1]


def test_iter_observed_numbers_filters_nan() -> None:
    data = [{"v": "nope"}, {"v": 2}]
    out = list(iter_observed_numbers(data, lambda d, *_: d["v"]))
    assert out == [2.0]


def test_first_observed() -> None:
    assert first_observed([]) is None
    assert first_observed([None, 1]) is None  # iterable yields None first
    assert first_observed([1, 2]) == 1


def test_index_helpers_skip_nondefinite() -> None:
    # Exercise the `not definite(v)` branches.
    assert leastIndex([float("nan"), 1]) == 1
    assert greatestIndex([float("nan"), 1]) == 1
