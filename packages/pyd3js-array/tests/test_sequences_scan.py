from __future__ import annotations

import pytest

from pyd3js_array.cross import cross
from pyd3js_array.descending import descending
from pyd3js_array.pairs import pairs
from pyd3js_array.scan import scan
from pyd3js_array.transpose import transpose
from pyd3js_array.zip import zip


def test_cross_default_and_reduce() -> None:
    assert cross([1, 2], ["a", "b"]) == [[1, "a"], [1, "b"], [2, "a"], [2, "b"]]
    assert cross([1, 2], [10, 20], lambda a, b: a + b) == [11, 21, 12, 22]


def test_pairs_default_and_reduce() -> None:
    assert pairs([1, 2, 3, 4]) == [[1, 2], [2, 3], [3, 4]]
    assert pairs([1, 2, 3, 4], lambda a, b: a * b) == [2, 6, 12]
    assert pairs([1]) == []


def test_zip_and_transpose() -> None:
    assert zip([1, 2], ["a", "b", "c"], [True, False]) == [
        [1, "a", True],
        [2, "b", False],
    ]
    assert zip() == []
    assert transpose([[1, 2, 3], ["a", "b", "c"]]) == [[1, "a"], [2, "b"], [3, "c"]]


def test_scan() -> None:
    assert scan([3, 1, 2]) == 1
    assert scan([3, 1, 2], descending) == 0
    assert scan([]) is None
    assert scan([1]) == 0


@pytest.mark.oracle
def test_phase7_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    js = oracle_eval(
        r"""(function(){
  return {
    cross: d3.cross([1,2],['a','b']),
    crossReduce: d3.cross([1,2],[10,20], (a,b)=>a+b),
    pairs: d3.pairs([1,2,3,4]),
    pairsReduce: d3.pairs([1,2,3,4], (a,b)=>a*b),
    zip: d3.zip([1,2],['a','b','c'],[true,false]),
    transpose: d3.transpose([[1,2,3],['a','b','c']]),
    scan: d3.scan([3,1,2]),
    scanDesc: d3.scan([3,1,2], d3.descending),
    scanEmpty: d3.scan([]),
    scanSingleton: d3.scan([1]),
  };
})()"""
    )

    assert cross([1, 2], ["a", "b"]) == js["cross"]
    assert cross([1, 2], [10, 20], lambda a, b: a + b) == js["crossReduce"]
    assert pairs([1, 2, 3, 4]) == js["pairs"]
    assert pairs([1, 2, 3, 4], lambda a, b: a * b) == js["pairsReduce"]
    assert zip([1, 2], ["a", "b", "c"], [True, False]) == js["zip"]
    assert transpose([[1, 2, 3], ["a", "b", "c"]]) == js["transpose"]
    assert scan([3, 1, 2]) == js["scan"]
    assert scan([3, 1, 2], descending) == js["scanDesc"]
    assert scan([]) == js["scanEmpty"]
    assert scan([1]) == js["scanSingleton"]
