"""Ports of d3-transition@3.0.1 ``active-test.js`` (virtual timer)."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition import active


def _with_virtual_time() -> callable:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return step


def test_active_null_name_variants_no_match() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)

    assert active(root) is None
    assert active(root, None) is None

    s.transition().delay(50).duration(50)
    s.transition("foo").duration(50)
    assert active(root) is None
    assert active(root, None) is None

    step(0)
    assert active(root) is None
    assert active(root, None) is None

    step(100)
    assert active(root) is None
    assert active(root, None) is None


def test_active_foo_name_no_match_when_other_runs() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)

    assert active(root, "foo") is None

    s.transition("foo").delay(50).duration(50)
    s.transition().duration(50)
    assert active(root, None) is None
    assert active(root, "foo") is None

    step(0)
    assert active(root, "foo") is None

    step(100)
    assert active(root, "foo") is None


def test_active_returns_running_null_named_transition() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    checks: list[int] = []

    def check(*_args) -> None:
        a = active(root)
        assert a is not None
        assert a._groups == [[root]]
        assert a._parents == [None]
        assert a._name is None
        assert a._id == t._id
        checks.append(len(checks))

    def tween_factory(*_args):
        check()
        def tick(this, tt: float) -> None:  # noqa: ANN001
            if tt >= 1:
                check()

        return tick

    t = select(root).transition().on("start", check).tween("tween", tween_factory).on("end", check)
    step(0)
    step(300)
    assert len(checks) >= 2


def test_active_returns_running_named_foo_transition() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    checks: list[int] = []

    def check(*_args) -> None:
        a = active(root, "foo")
        assert a is not None
        assert a._groups == [[root]]
        assert a._parents == [None]
        assert a._name == "foo"
        assert a._id == t._id
        checks.append(len(checks))

    def tween_factory(*_args):
        check()
        def tick(this, tt: float) -> None:  # noqa: ANN001
            if tt >= 1:
                check()

        return tick

    t = select(root).transition("foo").on("start", check).tween("tween", tween_factory).on("end", check)
    step(0)
    step(300)
    assert len(checks) >= 2
