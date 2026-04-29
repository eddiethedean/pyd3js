from __future__ import annotations

import pytest

from pyd3js_array.group import group
from pyd3js_array.groups import groups
from pyd3js_array.index import index
from pyd3js_array.indexes import indexes
from pyd3js_array.rollup import rollup
from pyd3js_array.rollups import rollups
from pyd3js_array.sum import sum_ as sum


def test_groups_and_group_basic() -> None:
    data = [{"k": "a", "v": 1}, {"k": "a", "v": 2}, {"k": "b", "v": 3}]
    g = group(data, lambda d: d["k"])
    assert list(g.keys()) == ["a", "b"]
    assert [x["v"] for x in g["a"]] == [1, 2]

    gs = groups(data, lambda d: d["k"])
    assert gs == [
        ["a", [{"k": "a", "v": 1}, {"k": "a", "v": 2}]],
        ["b", [{"k": "b", "v": 3}]],
    ]


def test_group_requires_key() -> None:
    with pytest.raises(TypeError):
        group([])  # type: ignore[call-arg]


def test_group_nested() -> None:
    data = [
        {"a": "x", "b": "y", "v": 1},
        {"a": "x", "b": "z", "v": 2},
        {"a": "w", "b": "y", "v": 3},
    ]
    gs = groups(data, lambda d: d["a"], lambda d: d["b"])
    assert gs == [
        [
            "x",
            [
                ["y", [{"a": "x", "b": "y", "v": 1}]],
                ["z", [{"a": "x", "b": "z", "v": 2}]],
            ],
        ],
        ["w", [["y", [{"a": "w", "b": "y", "v": 3}]]]],
    ]


def test_index_duplicate_key_raises() -> None:
    data = [{"k": "a", "v": 1}, {"k": "a", "v": 2}]
    with pytest.raises(ValueError, match="duplicate key"):
        index(data, lambda d: d["k"])


def test_index_requires_key() -> None:
    with pytest.raises(TypeError):
        index([])  # type: ignore[call-arg]


def test_index_and_indexes_basic() -> None:
    data = [{"k": "a", "v": 1}, {"k": "b", "v": 2}, {"k": "c", "v": 3}]
    i = index(data, lambda d: d["k"])
    assert list(i.keys()) == ["a", "b", "c"]
    assert i["b"]["v"] == 2

    is_ = indexes(data, lambda d: d["k"])
    assert is_ == [["a", data[0]], ["b", data[1]], ["c", data[2]]]


def test_index_nested() -> None:
    data = [
        {"a": "x", "b": "y", "v": 1},
        {"a": "x", "b": "z", "v": 2},
        {"a": "w", "b": "y", "v": 3},
    ]
    out = index(data, lambda d: d["a"], lambda d: d["b"])
    assert out["x"]["z"]["v"] == 2


def test_index_nested_duplicate_key_raises() -> None:
    data = [
        {"a": "x", "b": "y", "v": 1},
        {"a": "x", "b": "y", "v": 2},
    ]
    with pytest.raises(ValueError, match="duplicate key"):
        index(data, lambda d: d["a"], lambda d: d["b"])


def test_rollup_and_rollups() -> None:
    data = [{"k": "a", "v": 1}, {"k": "a", "v": 2}, {"k": "b", "v": 3}]
    r = rollup(data, lambda vs: sum(vs, lambda d, *_: d["v"]), lambda d: d["k"])
    assert r == {"a": 3.0, "b": 3.0}

    rs = rollups(data, lambda vs: sum(vs, lambda d, *_: d["v"]), lambda d: d["k"])
    assert rs == [["a", 3.0], ["b", 3.0]]


@pytest.mark.oracle
def test_group_index_rollup_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    expr = r"""(function(){
  function mapToPairs(m){
    if (m && typeof m.get === 'function' && typeof m.entries === 'function'){
      return Array.from(m.entries(), ([k,v]) => [k, mapToPairs(v)]);
    }
    return m;
  }
  const data=[{k:'a',v:1},{k:'a',v:2},{k:'b',v:3}];
  const dataUnique=[{k:'a',v:1},{k:'b',v:2},{k:'c',v:3}];

  const g=d3.group(data, d=>d.k);
  const gs=d3.groups(data, d=>d.k);

  const i=d3.index(dataUnique, d=>d.k);
  const is=d3.indexes(dataUnique, d=>d.k);

  const r=d3.rollup(data, v=>d3.sum(v, d=>d.v), d=>d.k);
  const rs=d3.rollups(data, v=>d3.sum(v, d=>d.v), d=>d.k);

  return {
    group: mapToPairs(g),
    groups: gs,
    index: mapToPairs(i),
    indexes: is,
    rollup: mapToPairs(r),
    rollups: rs,
  };
})()"""
    js = oracle_eval(expr)

    data = [{"k": "a", "v": 1}, {"k": "a", "v": 2}, {"k": "b", "v": 3}]
    data_unique = [{"k": "a", "v": 1}, {"k": "b", "v": 2}, {"k": "c", "v": 3}]

    assert groups(data, lambda d: d["k"]) == js["groups"]
    assert indexes(data_unique, lambda d: d["k"]) == js["indexes"]

    assert (
        rollups(data, lambda vs: sum(vs, lambda d, *_: d["v"]), lambda d: d["k"])
        == js["rollups"]
    )


@pytest.mark.oracle
def test_index_duplicate_key_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    expr = r"""(function(){
  try {
    d3.index([{k:'a'},{k:'a'}], d=>d.k);
    return 'no-error';
  } catch (e) {
    return String(e && e.message);
  }
})()"""
    js = oracle_eval(expr)
    assert js == "duplicate key"
