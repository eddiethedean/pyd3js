from __future__ import annotations

import builtins

import pytest

from pyd3js_array.bin import bin
from pyd3js_array.bisect import bisectCenter, bisectLeft, bisectRight
from pyd3js_array.cross import cross
from pyd3js_array.deviation import deviation
from pyd3js_array.difference import difference
from pyd3js_array.disjoint import disjoint
from pyd3js_array.extent import extent
from pyd3js_array.group_sort import groupSort
from pyd3js_array.intersection import intersection
from pyd3js_array.max import max_ as max
from pyd3js_array.mean import mean
from pyd3js_array.min import min_ as min
from pyd3js_array.nice import nice
from pyd3js_array.pairs import pairs
from pyd3js_array.permute import permute
from pyd3js_array.quantile import quantile
from pyd3js_array.quantile_sorted import quantileSorted
from pyd3js_array.quickselect import quickselect
from pyd3js_array.range import range_ as range
from pyd3js_array.rank import rank
from pyd3js_array.scan import scan
from pyd3js_array.shuffler import shuffler
from pyd3js_array.sort import sort
from pyd3js_array.subset import subset
from pyd3js_array.sum import sum_ as sum
from pyd3js_array.superset import superset
from pyd3js_array.tick_increment import tickIncrement
from pyd3js_array.tick_step import tickStep
from pyd3js_array.ticks import ticks
from pyd3js_array.transpose import transpose
from pyd3js_array.union import union
from pyd3js_array.variance import variance
from pyd3js_array.zip import zip


@pytest.mark.oracle
def test_oracle_more_json_safe_parity(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    # Core reducers / stats
    data = [None, "2", 3, "nope", True, 0]
    assert sum(data) == oracle_eval("(function(){ return d3.sum([null,'2',3,'nope',true,0]); })()")
    assert mean(data) == oracle_eval(
        "(function(){ return d3.mean([null,'2',3,'nope',true,0]); })()"
    )
    assert variance([1, 2, 3]) == oracle_eval("(function(){ return d3.variance([1,2,3]); })()")
    assert deviation([1, 2, 3]) == oracle_eval(
        "(function(){ return d3.deviation([1,2,3]); })()"
    )

    # Extent/min/max parity (JSON-safe; avoid Infinity/NaN)
    ex_py = extent([5, None, "2", 3])
    ex_js = oracle_eval("(function(){ return d3.extent([5,null,'2',3]); })()")
    assert (None if ex_py is None else list(ex_py)) == ex_js
    assert min([5, None, "2", 3]) == oracle_eval("(function(){ return d3.min([5,null,'2',3]); })()")
    assert max([5, None, "2", 3]) == oracle_eval("(function(){ return d3.max([5,null,'2',3]); })()")

    # Range/ticks/nice
    assert range(1, 5, 2) == oracle_eval("(function(){ return d3.range(1,5,2); })()")
    assert ticks(-1, 3, 4) == oracle_eval("(function(){ return d3.ticks(-1,3,4); })()")
    assert tickIncrement(0, 1, 5) == oracle_eval("(function(){ return d3.tickIncrement(0,1,5); })()")
    assert tickStep(10, 0, 5) == oracle_eval("(function(){ return d3.tickStep(10,0,5); })()")
    assert list(nice(0.2, 9.6, 5)) == oracle_eval("(function(){ return d3.nice(0.2,9.6,5); })()")

    # Quantiles
    assert quantile([1, 2, 3, 4], 0.25) == oracle_eval(
        "(function(){ return d3.quantile([1,2,3,4],0.25); })()"
    )
    assert quantileSorted([1, 2, 3, 4], 0.25) == oracle_eval(
        "(function(){ return d3.quantileSorted([1,2,3,4],0.25); })()"
    )

    # Bisect
    arr = [1, 2, 2, 2, 3]
    assert bisectLeft(arr, 2) == oracle_eval("(function(){ return d3.bisectLeft([1,2,2,2,3],2); })()")
    assert bisectRight(arr, 2) == oracle_eval("(function(){ return d3.bisectRight([1,2,2,2,3],2); })()")
    assert bisectCenter(arr, 2.4) == oracle_eval(
        "(function(){ return d3.bisectCenter([1,2,2,2,3],2.4); })()"
    )

    # Bin (compare boundaries + counts)
    b = bin().domain([0, 10]).thresholds([2, 4, 6, 8])
    py_bins = [{"x0": x.x0, "x1": x.x1, "n": len(x)} for x in b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]
    js_bins = oracle_eval(
        "(function(){ const b=d3.bin().domain([0,10]).thresholds([2,4,6,8]); const bins=b([0,1,2,3,4,5,6,7,8,9,10]); return bins.map(x=>({x0:x.x0,x1:x.x1,n:x.length})); })()"
    )
    assert py_bins == js_bins

    # Sets
    assert union([1, 2, 2], [2, 3], [3, 1]) == oracle_eval(
        "(function(){ return Array.from(d3.union([1,2,2],[2,3],[3,1])); })()"
    )
    assert intersection([1, 2, 2], [2, 3], [2, 4]) == oracle_eval(
        "(function(){ return Array.from(d3.intersection([1,2,2],[2,3],[2,4])); })()"
    )
    assert difference([1, 2, 3], [2, 4]) == oracle_eval(
        "(function(){ return Array.from(d3.difference([1,2,3],[2,4])); })()"
    )
    assert subset([2, 3], [1, 2, 3]) == oracle_eval("(function(){ return d3.subset([2,3],[1,2,3]); })()")
    assert superset([1, 2, 3], [2, 3]) == oracle_eval(
        "(function(){ return d3.superset([1,2,3],[2,3]); })()"
    )
    assert disjoint([1, 2], [3, 4]) == oracle_eval("(function(){ return d3.disjoint([1,2],[3,4]); })()")

    # Sorting/selection
    assert sort([3, 1, 2, 2]) == oracle_eval("(function(){ return d3.sort([3,1,2,2]); })()")
    assert permute(["a", "b", "c", "d"], [2, 0, 3]) == oracle_eval(
        "(function(){ return d3.permute(['a','b','c','d'],[2,0,3]); })()"
    )
    assert rank([10, 20, 20, 30]) == oracle_eval(
        "(function(){ return Array.from(d3.rank([10,20,20,30])); })()"
    )
    data2 = [{"k": "a", "v": 2}, {"k": "a", "v": 1}, {"k": "b", "v": 5}, {"k": "b", "v": 4}]
    assert groupSort(data2, lambda vs: builtins.min(d["v"] for d in vs), lambda d: d["k"]) == oracle_eval(
        "(function(){ const data=[{k:'a',v:2},{k:'a',v:1},{k:'b',v:5},{k:'b',v:4}]; return Array.from(d3.groupSort(data, v=>d3.min(v, d=>d.v), d=>d.k)); })()"
    )
    xs = [5, 1, 4, 3, 2]
    quickselect(xs, 2)
    assert xs == oracle_eval("(function(){ const x=[5,1,4,3,2]; d3.quickselect(x,2); return x; })()")

    # Sequences
    assert cross([1, 2], ["a", "b"]) == oracle_eval("(function(){ return d3.cross([1,2],['a','b']); })()")
    assert pairs([1, 2, 3, 4]) == oracle_eval("(function(){ return d3.pairs([1,2,3,4]); })()")
    assert zip([1, 2], ["a", "b", "c"], [True, False]) == oracle_eval(
        "(function(){ return d3.zip([1,2],['a','b','c'],[true,false]); })()"
    )
    assert transpose([[1, 2, 3], ["a", "b", "c"]]) == oracle_eval(
        "(function(){ return d3.transpose([[1,2,3],['a','b','c']]); })()"
    )
    assert scan([3, 1, 2]) == oracle_eval("(function(){ return d3.scan([3,1,2]); })()")

    # Random: deterministic shuffler parity
    seq = [0.9, 0.1, 0.5, 0.3, 0.7]
    it = iter(seq)

    def rng() -> float:
        return next(it)

    a = [1, 2, 3, 4, 5]
    shuffler(rng)(a, 0, 5)
    js = oracle_eval(
        r"""(function(){
  const seq = [0.9, 0.1, 0.5, 0.3, 0.7];
  let i = 0;
  function rng(){ return seq[i++]; }
  const a = [1,2,3,4,5];
  d3.shuffler(rng)(a, 0, 5);
  return a;
})()"""
    )
    assert a == js

