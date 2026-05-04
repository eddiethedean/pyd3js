"""Ports of d3-transition@3.0.1 ``index-test.js`` and ``transition-test.js``."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition import transition
from pyd3js_transition.transition.index import Transition


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


def test_transition_factory_default_targets_document_element() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = transition()
    schedule = root.__transition__[t._id]
    assert t.node() is root
    assert schedule["name"] is None


def test_transition_factory_none_targets_document_element() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = transition(None)
    schedule = root.__transition__[t._id]
    assert t.node() is root
    assert schedule["name"] is None


def test_transition_factory_named_transition() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = transition("foo")
    schedule = root.__transition__[t._id]
    assert t.node() is root
    assert schedule["name"] == "foo"


def test_transition_instances_are_transition_type() -> None:
    g.document = parse_html("<html><body></body></html>")
    t = transition()
    assert isinstance(t, Transition)


def test_transition_prototype_can_be_extended() -> None:
    g.document = parse_html("<html><body></body></html>")

    def test_method(self) -> int:  # noqa: ANN001
        return 42

    try:
        setattr(Transition, "test_method", test_method)
        t = transition()
        assert t.test_method() == 42
    finally:
        delattr(Transition, "test_method")


def test_chained_zero_duration_transitions_all_end() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    ended = {"a": False, "b": False, "c": False}

    t = s.transition().duration(0).on("end", lambda *_: ended.__setitem__("a", True))
    s.transition().duration(0).on("end", lambda *_: ended.__setitem__("b", True))
    t.transition().duration(0).on("end", lambda *_: ended.__setitem__("c", True))
    step(50)
    assert ended["a"] is True
    assert ended["b"] is True
    assert ended["c"] is True
