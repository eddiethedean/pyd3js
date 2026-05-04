from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_ease import easeCubicInOut
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


def _set_document_two_divs() -> None:
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


def test_transition_tween_defines_tween_using_interpolator_returned_by_value_factory() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    seen = {"v": None}

    def interpolate(_this, t: float) -> None:  # noqa: ANN001
        seen["v"] = t

    select(root).transition().tween("foo", lambda *_: interpolate)
    step(125)
    assert seen["v"] == pytest.approx(easeCubicInOut(125 / 250))


def test_transition_tween_invokes_value_with_expected_context_and_args() -> None:
    _set_document_two_divs()
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    result: list[list[object]] = []

    def value(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])
        return None

    selectAll([one, two]).data(["one", "two"]).transition().tween("foo", value)
    step(0)  # start / init tweens
    assert result == [
        ["one", 0, [one, two], one],
        ["two", 1, [one, two], two],
    ]


def test_transition_tween_passes_eased_time_to_interpolator() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    then = timer_engine.now()
    duration = 250.0
    ease = easeCubicInOut

    t = select(root).transition().tween("foo", lambda *_: interpolate)
    schedule = root.__transition__[t._id]

    def interpolate(this, tt: float) -> None:  # noqa: ANN001
        assert this is root
        expected = 1.0 if schedule["state"] == sched.ENDING else ease((timer_engine.now() - then) / duration)
        assert tt == pytest.approx(expected)

    step(0)
    step(300)
    assert getattr(root, "__transition__", None) is None


def test_transition_tween_allows_value_factory_to_return_none_for_noop() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    select(root).transition().tween("foo", lambda *_: None)


def test_transition_tween_uses_copy_on_write_for_updates() -> None:
    _set_document_two_divs()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    def foo_factory(*_args):
        return lambda *_: None

    def bar_factory(*_args):
        return lambda *_: None

    t = selectAll([one, two]).transition()
    schedule1 = one.__transition__[t._id]
    schedule2 = two.__transition__[t._id]

    t.tween("foo", foo_factory)
    assert schedule1["tween"] == [{"name": "foo", "value": foo_factory}]
    assert schedule2["tween"] is schedule1["tween"]

    t.tween("foo", bar_factory)
    assert schedule1["tween"] == [{"name": "foo", "value": bar_factory}]
    assert schedule2["tween"] is schedule1["tween"]

    select(two).transition(t).tween("foo", foo_factory)
    assert schedule1["tween"] == [{"name": "foo", "value": bar_factory}]
    assert schedule2["tween"] == [{"name": "foo", "value": foo_factory}]


def test_transition_tween_uses_copy_on_write_for_removals() -> None:
    _set_document_two_divs()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    def foo_factory(*_args):
        return lambda *_: None

    t = selectAll([one, two]).transition()
    schedule1 = one.__transition__[t._id]
    schedule2 = two.__transition__[t._id]

    t.tween("foo", foo_factory)
    assert schedule1["tween"] == [{"name": "foo", "value": foo_factory}]
    assert schedule2["tween"] is schedule1["tween"]

    t.tween("bar", None)
    assert schedule1["tween"] == [{"name": "foo", "value": foo_factory}]
    assert schedule2["tween"] is schedule1["tween"]

    t.tween("foo", None)
    assert schedule1["tween"] == []
    assert schedule2["tween"] is schedule1["tween"]

    select(two).transition(t).tween("foo", foo_factory)
    assert schedule1["tween"] == []
    assert schedule2["tween"] == [{"name": "foo", "value": foo_factory}]


def test_transition_tween_coerces_name_to_string_on_set_and_get() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement

    def tween_factory(*_args):
        return lambda *_: None

    class Name:
        def __str__(self) -> str:
            return "foo"

    t = select(root).transition().tween(Name(), tween_factory)
    assert t.tween("foo") is tween_factory
    assert t.tween(Name()) is tween_factory


def test_transition_tween_throws_if_value_not_none_and_not_callable() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises(Exception):
        t.tween("foo", 42)  # type: ignore[arg-type]


def test_transition_tween_name_none_removes_tween() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    frames = {"n": 0}

    def tick(this, _t: float) -> None:  # noqa: ANN001
        assert this is root
        frames["n"] += 1

    select(root).transition().tween("foo", lambda *_: tick).tween("foo", None)
    assert select(root).transition().tween("foo") is None  # separate transition has none
    step(125)
    assert frames["n"] == 0


def test_transition_tween_getter_returns_tween_function() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement

    def tween_factory(*_args):
        return lambda *_: None

    called = {"start": 0, "end": 0}

    def started(*_args) -> None:
        called["start"] += 1
        assert t.tween("foo") is tween_factory

    def ended(*_args) -> None:
        called["end"] += 1
        assert t.tween("foo") is tween_factory

    t = select(root).transition().tween("foo", tween_factory).on("start", started).on("end", ended)
    assert t.tween("foo") is tween_factory
    assert t.tween("bar") is None
    step(0)
    step(300)
    assert called["start"] == 1
    assert called["end"] == 1

