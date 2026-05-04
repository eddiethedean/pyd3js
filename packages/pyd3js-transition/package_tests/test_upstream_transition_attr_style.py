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


def test_transition_attr_interpolates_color_midway() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).attr("fill", "red")
    s.transition().delay(1).attr("fill", "blue")
    step(1)
    step(125)
    assert root.getAttribute("fill") == "rgb(128, 0, 128)"


def test_transition_attr_function_evaluated_immediately_with_expected_args() -> None:
    _set_document_two_divs()
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    result: list[list[object]] = []
    s = selectAll([one, two]).data(["red", "green"])

    def value(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])
        return d

    s.transition().attr("fill", value)
    assert result == [
        ["red", 0, [one, two], one],
        ["green", 1, [one, two], two],
    ]
    step(125)
    assert one.getAttribute("fill") is not None
    assert two.getAttribute("fill") is not None


def test_transition_attr_null_removes_attribute_post_start() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).attr("fill", "red")
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert root.getAttribute("fill") == "red"

    s.transition().attr("fill", None).on("start", on_start)
    step(0)
    assert started["ok"] is True
    step(1)
    assert root.hasAttribute("fill") is False


def test_transition_attr_constant_noop_if_string_coerced_matches_at_init() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).attr("foo", 1)
    s.transition().delay(1).attr("foo", 1)
    step(1)
    step(125)
    root.setAttribute("foo", "2")
    step(125)
    assert root.getAttribute("foo") == "2"


def test_transition_style_interpolates_color_midway() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).style("color", "red")
    s.transition().delay(1).style("color", "blue")
    step(1)
    step(125)
    assert root.style.getPropertyValue("color") == "rgb(128, 0, 128)"


def test_transition_style_function_evaluated_immediately_with_expected_args() -> None:
    _set_document_two_divs()
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    result: list[list[object]] = []
    s = selectAll([one, two]).data(["red", "green"])

    def value(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])
        return d

    s.transition().style("color", value)
    assert result == [
        ["red", 0, [one, two], one],
        ["green", 1, [one, two], two],
    ]
    step(125)
    assert one.style.getPropertyValue("color") != ""
    assert two.style.getPropertyValue("color") != ""


def test_transition_style_null_removes_style_post_start() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).style("color", "red")
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert root.style.getPropertyValue("color") == "red"

    s.transition().style("color", None).on("start", on_start)
    step(0)
    assert started["ok"] is True
    step(1)
    assert root.style.getPropertyValue("color") == ""


def test_transition_style_recycles_tweens_across_nodes() -> None:
    _set_document_two_divs()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().style("color", "red")
    assert one.__transition__[t._id]["tween"] is two.__transition__[t._id]["tween"]


def test_transition_style_constant_noop_if_string_coerced_matches_at_init() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).style("opacity", 1)
    s.transition().delay(1).style("opacity", 1)
    step(1)
    step(125)
    root.style.setProperty("opacity", "0.5")
    step(125)
    assert root.style.getPropertyValue("opacity") == "0.5"

