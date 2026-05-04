"""Ports of d3-transition@3.0.1 ``each-test.js`` (behavioral; no JS prototype identity)."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
from pyd3js_selection.selectAll import selectAll
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)


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


def test_transition_each_invokes_once_per_non_null_node() -> None:
    g.document = parse_html("<html><body></body></html>")
    _with_virtual_time()
    root = g.document.documentElement
    count = 0

    def cb(*_args) -> None:
        nonlocal count
        count += 1

    select(root).transition().each(cb)
    assert count == 1

    count = 0
    selectAll([None, root]).transition().each(cb)
    assert count == 1
