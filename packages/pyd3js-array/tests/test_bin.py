from __future__ import annotations

from collections.abc import Sequence

import pytest

from pyd3js_array.bin import _sturges, bin


def summarize_bins(bins: Sequence[Sequence[object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for b in bins:
        x0 = getattr(b, "x0")
        x1 = getattr(b, "x1")
        out.append({"x0": x0, "x1": x1, "n": len(b)})
    return out


def test_bin_default_simple() -> None:
    b = bin()
    bins = b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert summarize_bins(bins) == [
        {"x0": 0.0, "x1": 2.0, "n": 2},
        {"x0": 2.0, "x1": 4.0, "n": 2},
        {"x0": 4.0, "x1": 6.0, "n": 2},
        {"x0": 6.0, "x1": 8.0, "n": 2},
        {"x0": 8.0, "x1": 10.0, "n": 2},
    ]


def test_bin_custom_thresholds_list_and_domain() -> None:
    b = bin().domain([0, 10]).thresholds([2, 4, 6, 8])
    bins = b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert summarize_bins(bins) == [
        {"x0": 0.0, "x1": 2.0, "n": 2},
        {"x0": 2.0, "x1": 4.0, "n": 2},
        {"x0": 4.0, "x1": 6.0, "n": 2},
        {"x0": 6.0, "x1": 8.0, "n": 2},
        {"x0": 8.0, "x1": 10.0, "n": 3},
    ]


def test_bin_ignores_outside_domain() -> None:
    b = bin().domain([0, 10]).thresholds([2, 4, 6, 8])
    bins = b([-1, 0, 10, 11])
    assert summarize_bins(bins) == [
        {"x0": 0.0, "x1": 2.0, "n": 1},
        {"x0": 2.0, "x1": 4.0, "n": 0},
        {"x0": 4.0, "x1": 6.0, "n": 0},
        {"x0": 6.0, "x1": 8.0, "n": 0},
        {"x0": 8.0, "x1": 10.0, "n": 1},
    ]


def test_bin_value_accessor() -> None:
    b = bin().domain([0, 10]).thresholds([5])
    data = [{"v": 1}, {"v": 9}, {"v": 10}]
    b.value(lambda d: d["v"])
    bins = b(data)
    assert [len(x) for x in bins] == [1, 2]


def test_bin_getters_setters() -> None:
    b = bin()
    assert callable(b.value())
    assert b.domain() is None
    assert b.thresholds() is None

    b.value(lambda x: x).domain([0, 1]).thresholds(5)
    assert b.domain() is not None
    assert b.thresholds() == 5
    assert summarize_bins(b([0, 0.5, 1])) == [
        {"x0": 0.0, "x1": 0.2, "n": 1},
        {"x0": 0.2, "x1": 0.4, "n": 0},
        {"x0": 0.4, "x1": 0.6, "n": 1},
        {"x0": 0.6, "x1": 0.8, "n": 0},
        {"x0": 0.8, "x1": 1.0, "n": 1},
    ]


def test_bin_thresholds_callable() -> None:
    b = bin().domain([0, 10]).thresholds(lambda values, x0, x1: [5])
    bins = b([0, 4, 5, 10])
    assert summarize_bins(bins) == [
        {"x0": 0.0, "x1": 5.0, "n": 2},
        {"x0": 5.0, "x1": 10.0, "n": 2},
    ]


def test_bin_domain_callable() -> None:
    b = bin().domain(lambda values: (0, 10)).thresholds([5])
    bins = b([0, 4, 5, 10])
    assert summarize_bins(bins) == [
        {"x0": 0.0, "x1": 5.0, "n": 2},
        {"x0": 5.0, "x1": 10.0, "n": 2},
    ]


def test_bin_empty_after_filtering() -> None:
    b = bin()
    assert b([None, float("nan")]) == []


def test_sturges_edge() -> None:
    assert _sturges(0) == 1


def test_bin_constant_values() -> None:
    b = bin().thresholds(5)
    bins = b([1, 1, 1])
    assert summarize_bins(bins) == [{"x0": 1.0, "x1": 1.0, "n": 3}]


def test_bin_extent_updates_min() -> None:
    b = bin().thresholds(2)
    bins = b([3, 2, 1])
    assert bins[0].x0 == 1.0


@pytest.mark.oracle
def test_bin_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    py = summarize_bins(bin()(list(data)))
    js = oracle_eval(
        "(function(){ const b=d3.bin(); const bins=b([0,1,2,3,4,5,6,7,8,9]); return bins.map(x=>({x0:x.x0,x1:x.x1,n:x.length})); })()"
    )
    assert py == js


@pytest.mark.oracle
def test_bin_thresholds_and_domain_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    b = bin().domain([0, 10]).thresholds([2, 4, 6, 8])
    py = summarize_bins(b(list(data)))
    js = oracle_eval(
        "(function(){ const b=d3.bin().domain([0,10]).thresholds([2,4,6,8]); const bins=b([0,1,2,3,4,5,6,7,8,9,10]); return bins.map(x=>({x0:x.x0,x1:x.x1,n:x.length})); })()"
    )
    assert py == js
