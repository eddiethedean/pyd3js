from __future__ import annotations

import pytest

from pyd3js_array.difference import difference
from pyd3js_array.disjoint import disjoint
from pyd3js_array.intersection import intersection
from pyd3js_array.subset import subset
from pyd3js_array.superset import superset
from pyd3js_array.union import union


def test_union_order_unique() -> None:
    assert union([1, 2, 2], [2, 3], [3, 1]) == [1, 2, 3]


def test_intersection_order_unique() -> None:
    assert intersection([1, 2, 2], [2, 3], [2, 4]) == [2]


def test_intersection_empty_args() -> None:
    assert intersection() == []


def test_difference_order_unique() -> None:
    assert difference([1, 2, 3], [2, 4]) == [1, 3]


def test_subset_superset_disjoint() -> None:
    assert superset([1, 2, 3], [2, 3]) is True
    assert superset([1, 2], [1, 2, 3]) is False
    assert subset([2, 3], [1, 2, 3]) is True
    assert subset([1, 2, 3], [2, 3]) is False
    assert disjoint([1, 2], [3, 4]) is True
    assert disjoint([1, 2], [2, 3]) is False


@pytest.mark.oracle
def test_sets_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    js = oracle_eval(
        r"""(function(){
  function setToArray(s){ return Array.from(s); }
  return {
    union: setToArray(d3.union([1,2,2],[2,3],[3,1])),
    intersection: setToArray(d3.intersection([1,2,2],[2,3],[2,4])),
    difference: setToArray(d3.difference([1,2,3],[2,4])),
    superset1: d3.superset([1,2,3],[2,3]),
    superset2: d3.superset([1,2],[1,2,3]),
    subset1: d3.subset([2,3],[1,2,3]),
    subset2: d3.subset([1,2,3],[2,3]),
    disjoint1: d3.disjoint([1,2],[3,4]),
    disjoint2: d3.disjoint([1,2],[2,3]),
  };
})()"""
    )

    assert union([1, 2, 2], [2, 3], [3, 1]) == js["union"]
    assert intersection([1, 2, 2], [2, 3], [2, 4]) == js["intersection"]
    assert difference([1, 2, 3], [2, 4]) == js["difference"]
    assert superset([1, 2, 3], [2, 3]) == js["superset1"]
    assert superset([1, 2], [1, 2, 3]) == js["superset2"]
    assert subset([2, 3], [1, 2, 3]) == js["subset1"]
    assert subset([1, 2, 3], [2, 3]) == js["subset2"]
    assert disjoint([1, 2], [3, 4]) == js["disjoint1"]
    assert disjoint([1, 2], [2, 3]) == js["disjoint2"]

