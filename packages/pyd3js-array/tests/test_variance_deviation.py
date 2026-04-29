from __future__ import annotations

import json
import math

import pytest

from pyd3js_array.deviation import deviation
from pyd3js_array.variance import variance


def test_variance_basic() -> None:
    assert variance([1, 2, 3]) == 1
    assert variance([1, 2]) == 0.5


def test_variance_ignores_null_nan() -> None:
    assert variance([None, 1, 2, 3]) == 1
    assert variance([float("nan"), 1, 2, 3]) == 1


def test_variance_empty_or_single() -> None:
    assert variance([]) is None
    assert variance([1]) is None
    assert variance([None, float("nan"), 1]) is None


def test_deviation_basic() -> None:
    assert deviation([1, 2, 3]) == 1
    d = deviation([1, 2])
    assert d is not None
    assert math.isclose(d, math.sqrt(0.5))


def test_deviation_empty_or_single() -> None:
    assert deviation([]) is None
    assert deviation([1]) is None


@pytest.mark.oracle
def test_variance_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import assert_approx_oracle

    cases: list[list[object]] = [
        [],
        [1],
        [1, 2],
        [1, 2, 3],
        [None, 1, 2, 3],
        ["1", "2", "3"],
    ]
    for data in cases:
        py = variance(list(data))
        ex = f"(function(){{ return d3.variance({json.dumps(data)}); }})()"
        assert_approx_oracle(py, ex)


@pytest.mark.oracle
def test_deviation_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import assert_approx_oracle

    cases: list[list[object]] = [
        [],
        [1],
        [1, 2],
        [1, 2, 3],
        [None, 1, 2, 3],
        ["1", "2", "3"],
    ]
    for data in cases:
        py = deviation(list(data))
        ex = f"(function(){{ return d3.deviation({json.dumps(data)}); }})()"
        assert_approx_oracle(py, ex)
