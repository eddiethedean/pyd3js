from __future__ import annotations

import pytest

from pyd3js_array.flat_group import flatGroup
from pyd3js_array.flat_rollup import flatRollup


def test_flat_group_two_keys_shape() -> None:
    data = [{"a": "x", "b": 1}, {"a": "x", "b": 2}, {"a": "y", "b": 3}]
    out = flatGroup(data, lambda d: d["a"], lambda d: d["b"])
    assert out == [
        ["x", 1, [{"a": "x", "b": 1}]],
        ["x", 2, [{"a": "x", "b": 2}]],
        ["y", 3, [{"a": "y", "b": 3}]],
    ]


def test_flat_rollup_two_keys_shape() -> None:
    data = [{"a": "x", "b": 1}, {"a": "x", "b": 2}, {"a": "y", "b": 3}]
    out = flatRollup(data, lambda vs: len(vs), lambda d: d["a"], lambda d: d["b"])
    assert out == [["x", 1, 1], ["x", 2, 1], ["y", 3, 1]]


@pytest.mark.oracle
def test_flat_group_rollup_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    expr = """
    (function(){
      const data=[{a:'x',b:1},{a:'x',b:2},{a:'y',b:3}];
      return {
        fg: d3.flatGroup(data, d=>d.a, d=>d.b),
        fr: d3.flatRollup(data, vs=>vs.length, d=>d.a, d=>d.b),
      };
    })()
    """
    js = oracle_eval(expr)

    data = [{"a": "x", "b": 1}, {"a": "x", "b": 2}, {"a": "y", "b": 3}]
    assert flatGroup(data, lambda d: d["a"], lambda d: d["b"]) == js["fg"]
    assert flatRollup(data, lambda vs: len(vs), lambda d: d["a"], lambda d: d["b"]) == js["fr"]

