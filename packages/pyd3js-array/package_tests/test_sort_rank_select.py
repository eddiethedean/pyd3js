from __future__ import annotations

import pytest

from pyd3js_array.descending import descending
from pyd3js_array.group_sort import groupSort
from pyd3js_array.permute import permute
from pyd3js_array.quickselect import quickselect
from pyd3js_array.rank import rank
from pyd3js_array.sort import sort


def test_sort_basic() -> None:
    assert sort([3, 1, 2, 2]) == [1, 2, 2, 3]
    assert sort([3, 1, 2, 2], descending) == [3, 2, 2, 1]


def test_sort_accessor() -> None:
    data = [{"v": 2}, {"v": 1}, {"v": 2}]
    out = sort(data, lambda d: d["v"])
    assert [d["v"] for d in out] == [1, 2, 2]


def test_permute() -> None:
    assert permute(["a", "b", "c", "d"], [2, 0, 3]) == ["c", "a", "d"]


def test_rank() -> None:
    assert rank([10, 20, 20, 30]) == [0, 1, 1, 3]
    assert rank([10, 20, 20, 30], descending) == [3, 1, 1, 0]
    assert rank([]) == []


def test_group_sort() -> None:
    data = [
        {"k": "a", "v": 2},
        {"k": "a", "v": 1},
        {"k": "b", "v": 5},
        {"k": "b", "v": 4},
    ]
    out = groupSort(data, lambda vs: min(d["v"] for d in vs), lambda d: d["k"])
    assert out == ["a", "b"]


def test_group_sort_compare_branches() -> None:
    data = [{"k": "a", "v": 1}, {"k": "b", "v": 2}]
    assert groupSort(data, lambda vs: vs[0]["v"], lambda d: d["k"]) == ["a", "b"]
    assert groupSort(data, lambda vs: vs[0]["v"], lambda d: d["k"], descending) == [
        "b",
        "a",
    ]
    assert groupSort(data, lambda vs: 1, lambda d: d["k"]) == ["a", "b"]


def test_quickselect_partition_property() -> None:
    x = [5, 1, 4, 3, 2]
    quickselect(x, 2)
    pivot = x[2]
    assert all(v <= pivot for v in x[:2])
    assert all(v >= pivot for v in x[3:])


def test_quickselect_large_array_path() -> None:
    # Exercise the upstream Floyd–Rivest narrowing branch (>600 window).
    x = list(range(1000, 0, -1))
    quickselect(x, 500)
    assert x[500] == 501


def test_quickselect_out_of_bounds_is_noop() -> None:
    x = [3, 2, 1]
    quickselect(x, 10)
    assert x == [3, 2, 1]


def test_sort_comparator_arity_detection() -> None:
    def cmp(a, b):  # noqa: ANN001
        return -1 if a < b else (1 if a > b else 0)

    assert sort([2, 1], cmp) == [1, 2]


def test_sort_callable_without_code_object() -> None:
    class Cmp:
        def __call__(self, a, b):  # noqa: ANN001
            return -1 if a < b else (1 if a > b else 0)

    assert sort([2, 1], Cmp()) == [1, 2]


def test_sort_nan_compare_and_bad_signature() -> None:
    # Exercise NaN comparator coercion to 0.
    assert sort([float("nan"), 1], descending)[-1] == 1

    class BadSig:
        __signature__ = "nope"

        def __call__(self, a, b):  # noqa: ANN001
            return -1 if a < b else (1 if a > b else 0)

    assert sort([2, 1], BadSig()) == [1, 2]


@pytest.mark.oracle
def test_phase6_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    js = oracle_eval(
        r"""(function(){
  const a=[3,1,2,2];
  const s1=d3.sort(a);
  const s2=d3.sort(a, d3.descending);
  const s3=d3.sort([{v:2},{v:1},{v:2}], d=>d.v).map(d=>d.v);

  const perm = d3.permute(['a','b','c','d'], [2,0,3]);

  const ranked = Array.from(d3.rank([10, 20, 20, 30]));
  const rankedDesc = Array.from(d3.rank([10, 20, 20, 30], d3.descending));

  const grouped = Array.from(d3.groupSort([{k:'a',v:2},{k:'a',v:1},{k:'b',v:5},{k:'b',v:4}], v=>d3.min(v, d=>d.v), d=>d.k));

  const qs = (function(){
    const x=[5,1,4,3,2];
    d3.quickselect(x, 2);
    return x;
  })();

  return {s1, s2, s3, perm, ranked, rankedDesc, grouped, qs};
})()"""
    )

    assert sort([3, 1, 2, 2]) == js["s1"]
    assert sort([3, 1, 2, 2], descending) == js["s2"]
    assert [
        d["v"] for d in sort([{"v": 2}, {"v": 1}, {"v": 2}], lambda d: d["v"])
    ] == js["s3"]
    assert permute(["a", "b", "c", "d"], [2, 0, 3]) == js["perm"]
    assert rank([10, 20, 20, 30]) == js["ranked"]
    assert rank([10, 20, 20, 30], descending) == js["rankedDesc"]
    assert (
        groupSort(
            [
                {"k": "a", "v": 2},
                {"k": "a", "v": 1},
                {"k": "b", "v": 5},
                {"k": "b", "v": 4},
            ],
            lambda vs: min(d["v"] for d in vs),
            lambda d: d["k"],
        )
        == js["grouped"]
    )

    x = [5, 1, 4, 3, 2]
    quickselect(x, 2)
    assert x == js["qs"]
