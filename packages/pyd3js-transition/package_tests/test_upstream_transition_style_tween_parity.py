"""Ports of d3-transition@3.0.1 ``test/transition/styleTween-test.js`` (virtual timer)."""

from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_ease import easeCubicInOut
from pyd3js_interpolate import interpolate_hcl
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


def _two_divs() -> None:
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


def test_transition_style_tween_defines_style_tween_from_factory() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")
    select(root).transition().styleTween("color", lambda *_: h)
    step(125)
    assert root.style.getPropertyValue("color") == h(easeCubicInOut(125 / 250))
    assert root.style.getPropertyPriority("color") == ""


def test_transition_style_tween_priority_important() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")
    select(root).transition().styleTween("color", lambda *_: h, "important")
    step(125)
    assert root.style.getPropertyValue("color") == h(easeCubicInOut(125 / 250))
    assert root.style.getPropertyPriority("color") == "important"


def test_transition_style_tween_invokes_factory_with_expected_context_and_args() -> None:
    _two_divs()
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    result: list[list[object]] = []

    def factory(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])
        return None

    selectAll([one, two]).data(["one", "two"]).transition().styleTween("color", factory)
    step(0)
    assert result == [
        ["one", 0, [one, two], one],
        ["two", 1, [one, two], two],
    ]


def test_transition_style_tween_passes_eased_time_to_interpolator() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    then = timer_engine.now()
    duration = 250.0
    ease = easeCubicInOut
    t = select(root).transition().styleTween("color", lambda *_: interpolate)
    schedule = root.__transition__[t._id]

    def interpolate(this, tt: float) -> str:  # noqa: ANN001
        assert this is root
        expected = 1.0 if schedule["state"] == sched.ENDING else ease((timer_engine.now() - then) / duration)
        assert tt == pytest.approx(expected)
        return "transparent"

    step(0)
    step(300)
    assert getattr(root, "__transition__", None) is None


def test_transition_style_tween_factory_returns_none_for_noop() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).style("color", "red")
    select(root).transition().styleTween("color", lambda *_: None)
    step(125)
    assert root.style.getPropertyValue("color") == "red"


def test_transition_style_tween_coerces_name_to_string() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")

    class Name:
        def __str__(self) -> str:
            return "color"

    select(root).transition().styleTween(Name(), lambda *_: h)
    step(125)
    assert root.style.getPropertyValue("color") == h(easeCubicInOut(125 / 250))


def test_transition_style_tween_throws_if_value_not_null_and_not_callable() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises(RuntimeError):
        t.styleTween("color", 42)  # type: ignore[arg-type]


def test_transition_style_tween_null_removes_tween() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")
    tr = select(root).transition().styleTween("color", lambda *_: h).styleTween("color", None)
    assert tr.styleTween("color") is None
    assert tr.tween("style.color") is None
    step(125)
    assert root.style.getPropertyValue("color") == ""


def test_transition_style_tween_getter_returns_factory_and_survives_start_end() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")

    def tween_factory(*_args):
        return h

    called = {"start": 0, "end": 0}

    def started(*_args) -> None:
        called["start"] += 1
        assert tr.styleTween("color") is tween_factory

    def ended(*_args) -> None:
        called["end"] += 1
        assert tr.styleTween("color") is tween_factory

    tr = select(root).transition().styleTween("color", tween_factory).on("start", started).on("end", ended)
    assert tr.styleTween("color") is tween_factory
    assert tr.styleTween("bar") is None
    step(0)
    step(300)
    assert called["start"] == 1
    assert called["end"] == 1


def test_transition_style_tween_getter_coerces_name_to_string() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement

    def tween_factory(*_args):
        return interpolate_hcl("red", "blue")

    class Name:
        def __str__(self) -> str:
            return "color"

    tr = select(root).transition().styleTween("color", tween_factory)
    assert tr.styleTween(Name()) is tween_factory
