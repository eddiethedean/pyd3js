"""Ports of d3-transition@3.0.1 root ``interrupt-test.js`` using ``interrupt(node, …)``."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition import interrupt


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


def test_interrupt_node_cancels_pending_transitions() -> None:
    g.document = parse_html("<html><body></body></html>")
    _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition()
    t2 = t1.transition()
    assert t1._id in root.__transition__
    assert t2._id in root.__transition__
    interrupt(root)
    assert getattr(root, "__transition__", None) is None


def test_interrupt_name_only_cancels_matching_name() -> None:
    g.document = parse_html("<html><body></body></html>")
    _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition("foo")
    t2 = s.transition()
    assert t1._id in root.__transition__
    assert t2._id in root.__transition__
    interrupt(root, "foo")
    assert t1._id not in root.__transition__
    assert t2._id in root.__transition__
