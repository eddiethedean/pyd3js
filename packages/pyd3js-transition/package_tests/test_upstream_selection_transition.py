from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_ease import easeBounce, easeCubicInOut
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
from pyd3js_selection.selectAll import selectAll
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
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


def _set_document() -> None:
    doc = parse_html(
        """
        <html>
          <body>
            <div id="one"><span></span></div>
            <div id="two"><span></span></div>
          </body>
        </html>
        """
    )
    g.document = doc


def test_selection_transition_returns_transition_instance() -> None:
    _set_document()
    root = g.document.documentElement
    t = select(root).transition()
    assert isinstance(t, Transition)


def test_selection_transition_uses_default_timing_parameters() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement

    t = select(root).transition()
    schedule = root.__transition__[t._id]

    assert schedule["time"] == pytest.approx(timer_engine.now())
    assert schedule["delay"] == 0.0
    assert schedule["duration"] == 250.0
    assert schedule["ease"] == easeCubicInOut

    step(1)


def test_selection_transition_assigns_monotonic_increasing_id() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition()
    t2 = s.transition()
    t3 = s.transition()
    assert t2._id > t1._id
    assert t3._id > t2._id


def test_selection_transition_default_name_is_none() -> None:
    _set_document()
    root = g.document.documentElement
    t = select(root).transition()
    schedule = root.__transition__[t._id]
    assert schedule["name"] is None


def test_selection_transition_none_name_is_none() -> None:
    _set_document()
    root = g.document.documentElement
    t = select(root).transition(None)
    schedule = root.__transition__[t._id]
    assert schedule["name"] is None


def test_selection_transition_name_uses_specified_name() -> None:
    _set_document()
    root = g.document.documentElement
    t = select(root).transition("foo")
    schedule = root.__transition__[t._id]
    assert schedule["name"] == "foo"


def test_selection_transition_name_coerces_to_string() -> None:
    _set_document()
    root = g.document.documentElement

    class Name:
        def __str__(self) -> str:
            return "foo"

    t = select(root).transition(Name())
    schedule = root.__transition__[t._id]
    assert schedule["name"] == "foo"


def test_selection_transition_transition_inherits_from_corresponding_parent() -> None:
    _set_document()
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    s = selectAll([one, two])
    t = s.transition().delay(lambda _d, i, _n: i * 50).duration(100).ease(easeBounce)

    schedule1 = one.__transition__[t._id]
    schedule2 = two.__transition__[t._id]

    t1b = select(one.firstChild).transition(t)
    schedule1b = one.firstChild.__transition__[t._id]
    assert t1b._id == t._id
    assert schedule1b["name"] == schedule1["name"]
    assert schedule1b["delay"] == schedule1["delay"]
    assert schedule1b["duration"] == schedule1["duration"]
    assert schedule1b["ease"] == schedule1["ease"]
    assert schedule1b["time"] == schedule1["time"]

    step(10)

    t2b = select(two.firstChild).transition(t)
    schedule2b = two.firstChild.__transition__[t._id]
    assert t2b._id == t._id
    assert schedule2b["name"] == schedule2["name"]
    assert schedule2b["delay"] == schedule2["delay"]
    assert schedule2b["duration"] == schedule2["duration"]
    assert schedule2b["ease"] == schedule2["ease"]
    assert schedule2b["time"] == schedule2["time"]


def test_selection_transition_transition_reselects_existing_transition_if_present() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)

    def foo_factory(*_args):
        return lambda *_: None

    def bar_factory(*_args):
        return lambda *_: None

    t1 = s.transition().tween("tween", foo_factory)
    schedule1 = root.__transition__[t1._id]
    t2 = s.transition(t1).tween("tween", bar_factory)
    schedule2 = root.__transition__[t2._id]
    assert t1._id == t2._id
    assert schedule1 is schedule2
    assert t1.tween("tween") is bar_factory
    assert t2.tween("tween") is bar_factory


def test_selection_transition_transition_throws_if_not_found() -> None:
    _set_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = select(one).transition()
    t2 = select(two).transition().delay(50)
    with pytest.raises(RuntimeError, match=r"transition .* not found"):
        select(two).transition(t1)
    with pytest.raises(RuntimeError, match=r"transition .* not found"):
        select(one).transition(t2)

