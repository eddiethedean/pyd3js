from __future__ import annotations

import pytest

from pyd3js_dispatch import dispatch
from tests.oracle.client import oracle_eval
from tests.util.normalize import assert_deep_equal


@pytest.mark.oracle
def test_oracle_on_set_get_remove_namespaces(require_oracle: None) -> None:
    expr = r"""(function(){
      const d = d3.dispatch("t");
      const log = [];
      d.on("t.a", function(x){ log.push(["a", x]); });
      d.on("t.b", function(x){ log.push(["b", x]); });
      d.call("t", null, 1);
      const gotA = d.on("t.a") != null;
      d.on("t.a", null);
      d.call("t", null, 2);
      return { log, gotA };
    })()"""
    expected = oracle_eval(expr)

    d = dispatch("t")
    log: list[list[object]] = []
    d.on("t.a", lambda _this, x: log.append(["a", x]))
    d.on("t.b", lambda _this, x: log.append(["b", x]))
    d.call("t", None, 1)
    got_a = d.on("t.a") is not None
    d.on("t.a", None)
    d.call("t", None, 2)

    assert_deep_equal({"log": log, "gotA": got_a}, expected)


@pytest.mark.oracle
def test_oracle_remove_across_all_types_with_dot_namespace(
    require_oracle: None,
) -> None:
    expr = r"""(function(){
      const d = d3.dispatch("a","b");
      const log = [];
      d.on("a.ns", function(){ log.push("a"); });
      d.on("b.ns", function(){ log.push("b"); });
      d.on(".ns", null);
      d.call("a", null);
      d.call("b", null);
      return log;
    })()"""
    expected = oracle_eval(expr)

    d = dispatch("a", "b")
    log: list[str] = []
    d.on("a.ns", lambda *_: log.append("a"))
    d.on("b.ns", lambda *_: log.append("b"))
    d.on(".ns", None)
    d.call("a", None)
    d.call("b", None)

    assert_deep_equal(log, expected)


@pytest.mark.oracle
def test_oracle_copy_isolation(require_oracle: None) -> None:
    expr = r"""(function(){
      const d = d3.dispatch("t");
      d.on("t.ns", function(){});
      const c = d.copy();
      c.on("t.ns", null);
      return { origHas: d.on("t.ns") != null, copyHas: c.on("t.ns") != null };
    })()"""
    expected = oracle_eval(expr)

    d = dispatch("t")
    d.on("t.ns", lambda *_: None)
    c = d.copy()
    c.on("t.ns", None)

    assert_deep_equal(
        {"origHas": d.on("t.ns") is not None, "copyHas": c.on("t.ns") is not None},
        expected,
    )
