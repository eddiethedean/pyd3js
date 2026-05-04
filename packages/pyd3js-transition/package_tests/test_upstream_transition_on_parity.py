"""Ports of d3-transition@3.0.1 ``on-test.js`` (virtual timer)."""

from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
from pyd3js_selection.selectAll import selectAll
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition.transition import schedule as sched


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


def _two_div_html() -> None:
    g.document = parse_html(
        """
        <html>
          <body>
            <div id="one"></div>
            <div id="two"></div>
          </body>
        </html>
        """
    )


def test_on_setter_rejects_non_callable_listener() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises((TypeError, ValueError)):
        t.on("start", 42)  # type: ignore[arg-type]


def test_on_getter_returns_registered_listeners() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement

    def foo(*_args) -> None:
        return None

    def bar(*_args) -> None:
        return None

    t = select(root).transition().on("start", foo).on("start.bar", bar)
    assert t.on("start") is foo
    assert t.on("start.foo") is None
    assert t.on("start.bar") is bar
    assert t.on("end") is None


def test_on_getter_unknown_event_type_raises() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises(ValueError):
        t.on("foo")


def test_on_setter_unknown_event_type_raises() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises(ValueError):
        t.on("foo", lambda *_: None)


def test_on_setter_unknown_listener_type_raises() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises((TypeError, ValueError)):
        t.on("start", 42)  # type: ignore[arg-type]


def test_on_null_removes_listener() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    starts = {"n": 0}
    t = select(root).transition().on("start.foo", lambda *_: starts.__setitem__("n", starts["n"] + 1))
    schedule = root.__transition__[t._id]
    assert t.on("start.foo", None) is t
    assert t.on("start.foo") is None
    assert schedule["on"].on("start.foo") is None
    step(50)
    assert starts["n"] == 0


def test_on_start_fires_in_starting_state() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    t = select(root).transition()
    schedule = root.__transition__[t._id]
    seen = {"ok": False}

    def on_start(*_args) -> None:
        assert schedule["state"] == sched.STARTING
        seen["ok"] = True

    t.on("start", on_start)
    step(0)
    assert seen["ok"] is True


def test_on_interrupt_while_running() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    t = s.transition()
    schedule = root.__transition__[t._id]
    seen = {"ok": False}

    def on_interrupt(*_args) -> None:
        assert schedule["state"] == sched.ENDED
        seen["ok"] = True

    t.on("interrupt", on_interrupt)
    step(1)
    s.interrupt()
    step(0)
    assert seen["ok"] is True


def test_on_interrupt_after_delay_while_running() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    t = s.transition()
    schedule = root.__transition__[t._id]
    seen = {"ok": False}

    def on_interrupt(*_args) -> None:
        assert schedule["state"] == sched.ENDED
        seen["ok"] = True

    t.on("interrupt", on_interrupt)
    step(50)
    s.interrupt()
    step(0)
    assert seen["ok"] is True


def test_on_end_fires_in_ending_state() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    t = select(root).transition().duration(50)
    schedule = root.__transition__[t._id]
    seen = {"ok": False}

    def on_end(*_args) -> None:
        assert schedule["state"] == sched.ENDING
        seen["ok"] = True

    t.on("end", on_end)
    step(0)
    step(50)
    assert seen["ok"] is True


def test_on_copy_on_write_across_nodes() -> None:
    _two_div_html()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    def foo(*_args) -> None:
        return None

    def bar(*_args) -> None:
        return None

    t = selectAll([one, two]).transition()
    schedule1 = one.__transition__[t._id]
    schedule2 = two.__transition__[t._id]
    t.on("start", foo)
    assert schedule1["on"].on("start") is foo
    assert schedule2["on"].on("start") is foo
    t.on("start", bar)
    assert schedule1["on"].on("start") is bar
    assert schedule2["on"].on("start") is bar
    select(two).transition(t).on("start", foo)
    assert schedule1["on"].on("start") is bar
    assert schedule2["on"].on("start") is foo
