from __future__ import annotations

import pytest

from pyd3js_array.every import every
from pyd3js_array.filter import filter
from pyd3js_array.map import map
from pyd3js_array.merge import merge
from pyd3js_array.reduce import reduce
from pyd3js_array.reverse import reverse
from pyd3js_array.some import some


def test_map_calls_mapper_with_index_and_values() -> None:
    data = ["a", "b", "c"]
    out = map(data, lambda v, i, values: f"{i}:{v}:{len(list(values))}")
    assert out == ["0:a:3", "1:b:3", "2:c:3"]


def test_filter_uses_test_predicate() -> None:
    data = [0, 1, 2, 3, 4]
    assert filter(data, lambda v, i, values: v % 2 == 0) == [0, 2, 4]


def test_every_some_short_circuit() -> None:
    data = [1, 2, 3, 4]
    assert every(data, lambda v, i, values: v < 10) is True
    assert every(data, lambda v, i, values: v < 3) is False
    assert some(data, lambda v, i, values: v == 3) is True
    assert some(data, lambda v, i, values: v == 999) is False


def test_reverse_returns_new_list() -> None:
    data = (1, 2, 3)
    assert reverse(data) == [3, 2, 1]


def test_merge_flattens_one_level() -> None:
    assert merge([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]


def test_reduce_without_initial_value() -> None:
    assert reduce([1, 2, 3], lambda acc, v, i, values: acc + v) == 6
    assert reduce([], lambda acc, v, i, values: acc + v) is None


def test_reduce_with_initial_value() -> None:
    assert reduce([1, 2, 3], lambda acc, v, i, values: acc + v, 10) == 16


@pytest.mark.oracle
def test_iterable_utils_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    assert map([1, 2, 3], lambda v, i, values: v * 2) == oracle_eval(
        "(function(){ return d3.map([1,2,3], (v,i)=>v*2); })()"
    )
    assert filter([1, 2, 3, 4, 5], lambda v, i, values: v % 2 == 1) == oracle_eval(
        "(function(){ return d3.filter([1,2,3,4,5], (v,i)=>v%2===1); })()"
    )
    assert every([1, 2, 3], lambda v, i, values: v > 0) == oracle_eval(
        "(function(){ return d3.every([1,2,3], (v,i)=>v>0); })()"
    )
    assert some([1, 2, 3], lambda v, i, values: v == 2) == oracle_eval(
        "(function(){ return d3.some([1,2,3], (v,i)=>v===2); })()"
    )
    assert reverse([1, 2, 3]) == oracle_eval("(function(){ return d3.reverse([1,2,3]); })()")
    assert merge([[1, 2], [3, 4]]) == oracle_eval("(function(){ return d3.merge([[1,2],[3,4]]); })()")
    assert reduce([1, 2, 3], lambda acc, v, i, values: acc + v) == oracle_eval(
        "(function(){ return d3.reduce([1,2,3], (acc,v,i)=>acc+v); })()"
    )
    assert reduce([1, 2, 3], lambda acc, v, i, values: acc + v, 10) == oracle_eval(
        "(function(){ return d3.reduce([1,2,3], (acc,v,i)=>acc+v, 10); })()"
    )

