"""Ports of d3-transition@3.0.1 ``text-test.js`` and ``textTween-test.js`` (virtual timer)."""

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


def _two_div_document() -> None:
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


def test_transition_text_constant_sets_content_after_transition() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert str(root.textContent or "") == ""

    t = select(root).transition().text("hello").on("start", on_start)
    step(0)
    assert started["ok"] is True
    step(300)
    assert root.textContent == "hello"
    # allow extra user data on transition object
    _ = t


def test_transition_text_function_sets_content() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert str(root.textContent or "") == ""

    t = select(root).transition().text(lambda *_: "hello").on("start", on_start)
    step(0)
    assert started["ok"] is True
    step(300)
    assert root.textContent == "hello"
    _ = t


def test_transition_text_function_evaluated_with_expected_context() -> None:
    _two_div_document()
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    result: list[list[object]] = []
    s = selectAll([one, two]).data(["red", "green"])

    def value(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])
        return d

    t = s.transition().text(value)
    assert result == [
        ["red", 0, [one, two], one],
        ["green", 1, [one, two], two],
    ]
    started = {"n": 0}

    def on_start(*_args) -> None:
        started["n"] += 1

    t.on("start", on_start)
    step(0)
    assert started["n"] == 2  # one start event per selected element (upstream behavior)
    step(300)
    assert one.textContent == "red"
    assert two.textContent == "green"


def test_transition_tween_text_invokes_stored_factory() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    t = select(root).transition().text("hello")
    step(0)
    fn = t.tween("text")
    assert fn is not None
    # factory(node, d, i, group) sets text when invoked like the schedule does
    fn(root, getattr(root, "__data__", None), 0, [root])
    assert root.textContent == "hello"
    step(300)
    assert root.textContent == "hello"


def test_transition_text_tween_interpolates_like_upstream() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")
    select(root).transition().textTween(lambda *_: h)
    step(125)
    assert root.textContent == h(easeCubicInOut(125 / 250))


def test_transition_text_tween_getter_returns_factory() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement

    def factory(*_args):
        return None

    t = select(root).transition().textTween(factory)
    assert t.textTween() is factory


def test_transition_text_tween_none_removes_tween() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement

    def factory(*_args):
        return None

    t = select(root).transition().textTween(factory).textTween(None)
    assert t.textTween() is None
