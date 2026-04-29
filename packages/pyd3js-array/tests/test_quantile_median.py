from __future__ import annotations

import json

import pytest

from pyd3js_array.median import median
from pyd3js_array.quantile import quantile
from pyd3js_array.quantile_sorted import quantileSorted


def test_quantile_basic() -> None:
    assert quantile([1, 2, 3, 4], 0.25) == 1.75
    assert quantile([1, 2, 3, 4], 0.5) == 2.5
    assert quantile([1, 2, 3, 4], 0.75) == 3.25


def test_quantile_clamps() -> None:
    assert quantile([1, 2, 3, 4], -0.1) == 1
    assert quantile([1, 2, 3, 4], 1.1) == 4


def test_quantile_filters_null_nan() -> None:
    assert quantile([None, 1, 2, float("nan")], 0.5) == 1.5


def test_quantile_empty() -> None:
    assert quantile([], 0.5) is None


def test_quantile_sorted_basic() -> None:
    assert quantileSorted([1, 2, 3, 4], 0.25) == 1.75
    assert quantileSorted([1, 2, 3, 4], 0.5) == 2.5


def test_median() -> None:
    assert median([1, 2, 3]) == 2
    assert median([1, 2, 3, 4]) == 2.5


@pytest.mark.oracle
def test_quantile_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import assert_approx_oracle

    cases = [
        ([1, 2, 3, 4], 0.25),
        ([1, 2, 3, 4], 0.5),
        ([1, 2, 3, 4], 0.75),
        ([1, 2, 3, 4], -0.1),
        ([1, 2, 3, 4], 1.1),
        ([], 0.5),
        ([None, 1, 2, float("nan")], 0.5),
    ]
    for data, p in cases:
        py = quantile(list(data), p)
        ex = f"(function(){{ return d3.quantile({json.dumps(data)}, {json.dumps(p)}); }})()"
        assert_approx_oracle(py, ex)


@pytest.mark.oracle
def test_quantile_sorted_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import assert_approx_oracle

    cases = [
        ([1, 2, 3, 4], 0.25),
        ([1, 2, 3, 4], 0.5),
        ([1, 2, 3, 4], 0.75),
    ]
    for data, p in cases:
        py = quantileSorted(list(data), p)
        ex = f"(function(){{ return d3.quantileSorted({json.dumps(data)}, {json.dumps(p)}); }})()"
        assert_approx_oracle(py, ex)


@pytest.mark.oracle
def test_median_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import assert_approx_oracle

    cases: list[list[object]] = [
        [],
        [1],
        [1, 2, 3],
        [1, 2, 3, 4],
        [None, 1, 2, float("nan")],
    ]
    for data in cases:
        py = median(list(data))
        ex = f"(function(){{ return d3.median({json.dumps(data)}); }})()"
        assert_approx_oracle(py, ex)
