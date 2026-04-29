from __future__ import annotations

import math

import pytest

from pyd3js_array.bisect import bisect
from pyd3js_array.count import count
from pyd3js_array.max_index import maxIndex
from pyd3js_array.median_index import medianIndex
from pyd3js_array.min_index import minIndex
from pyd3js_array.mode import mode
from pyd3js_array.quantile_index import quantileIndex


def test_count_ignores_none_and_nan_like() -> None:
    assert count([None, "2", 3, "nope", True, 0, float("nan")]) == 4  # 2,3,1,0


def test_min_max_index_basic() -> None:
    data = [None, 5, 2, 2, 9]
    assert minIndex(data) == 2
    assert maxIndex(data) == 4


def test_min_max_index_all_invalid() -> None:
    assert minIndex([None, float("nan")]) == -1
    assert maxIndex([None, float("nan")]) == -1


def test_mode_prefers_first_encountered_on_ties() -> None:
    assert mode([1, 2, 2, 1]) == 1
    assert mode([None, float("nan")]) is None


def test_quantile_index_empty_and_nan_p() -> None:
    assert quantileIndex([], 0.5) is None
    assert quantileIndex([1, 2, 3], float("nan")) is None


def test_median_index_delegates_to_quantile_index() -> None:
    assert medianIndex([10, 0, 5, 1]) == quantileIndex([10, 0, 5, 1], 0.5)


def test_bisect_aliases_right() -> None:
    assert bisect([1, 2, 2, 3], 2) == 3


@pytest.mark.oracle
def test_count_indices_mode_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    # count
    assert count([None, "2", 3, "nope", True, 0]) == oracle_eval(
        "(function(){ return d3.count([null,'2',3,'nope',true,0]); })()"
    )

    # bisect alias
    assert bisect([1, 2, 2, 2, 3], 2) == oracle_eval(
        "(function(){ return d3.bisect([1,2,2,2,3], 2); })()"
    )

    # minIndex/maxIndex (JSON-safe)
    assert minIndex([None, 5, 2, 2, 9]) == oracle_eval(
        "(function(){ return d3.minIndex([null,5,2,2,9]); })()"
    )
    assert maxIndex([None, 5, 2, 2, 9]) == oracle_eval(
        "(function(){ return d3.maxIndex([null,5,2,2,9]); })()"
    )

    # mode
    assert mode([1, 2, 2, 1]) == oracle_eval("(function(){ return d3.mode([1,2,2,1]); })()")

    # quantileIndex / medianIndex
    data = [None, "2", 3, "nope", True, 0]
    assert quantileIndex(data, 0.25) == oracle_eval(
        "(function(){ return d3.quantileIndex([null,'2',3,'nope',true,0], 0.25); })()"
    )
    assert medianIndex(data) == oracle_eval(
        "(function(){ return d3.medianIndex([null,'2',3,'nope',true,0]); })()"
    )

