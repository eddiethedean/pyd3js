from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_ease import easeCubicInOut
from pyd3js_interpolate import (
    interpolate_hcl,
    interpolate_number,
    interpolate_rgb,
    interpolate_string,
)
from pyd3js_selection.selectAll import selectAll
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
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


def test_transition_attr_namespaced_function_returns_blue_midway() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    uri = "http://www.w3.org/2000/svg"
    select(root).attr("svg:fill", "red")
    select(root).transition().delay(1).attr("svg:fill", lambda *_: "blue")
    step(1)
    step(125)
    t = easeCubicInOut(125 / 250)
    assert root.getAttributeNS(uri, "fill") == interpolate_rgb("red", "blue")(t)


def test_transition_attr_namespaced_constant_noop_when_coerced_matches() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    uri = "http://www.w3.org/2000/svg"
    select(root).attr("svg:foo", 1)
    select(root).transition().delay(1).attr("svg:foo", 1)
    step(1)
    step(125)
    root.setAttributeNS(uri, "foo", "2")
    step(125)
    assert root.getAttributeNS(uri, "foo") == "2"


def test_transition_attr_namespaced_function_noop_when_coerced_matches() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    uri = "http://www.w3.org/2000/svg"
    select(root).attr("svg:foo", 1)
    select(root).transition().delay(1).attr("svg:foo", lambda *_: 1)
    step(1)
    step(125)
    root.setAttributeNS(uri, "foo", "2")
    step(125)
    assert root.getAttributeNS(uri, "foo") == "2"


def test_transition_attr_namespaced_fill_midway() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root).attr("svg:fill", "red")
    s.transition().delay(1).attr("svg:fill", "blue")
    step(1)
    step(125)
    uri = "http://www.w3.org/2000/svg"
    assert root.getAttributeNS(uri, "fill") == "rgb(128, 0, 128)"


def test_transition_attr_function_number_from_px_string_yields_nan_string() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).attr("foo", "15px").transition().delay(1).attr("foo", lambda *_: 10)
    step(1)
    step(125)
    v = root.getAttribute("foo")
    assert v is not None and str(v).lower() == "nan"


def test_transition_attr_number_from_px_string_yields_nan_string() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).attr("foo", "15px").transition().delay(1).attr("foo", 10)
    step(1)
    step(125)
    v = root.getAttribute("foo")
    assert v is not None and str(v).lower() == "nan"


def test_transition_attr_interpolates_number_string_and_color() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    ease = easeCubicInOut
    duration = 250.0

    select(root).attr("n", "1").transition().delay(1).attr("n", 2)
    step(1)
    step(125)
    t = ease(125 / duration)
    assert str(root.getAttribute("n")) == str(interpolate_number(1, 2)(t))

    select(root).attr("s", "1px").transition().delay(1).attr("s", "2px")
    step(1)
    step(125)
    assert root.getAttribute("s") == interpolate_string("1px", "2px")(t)

    select(root).attr("c", "#f00").transition().delay(1).attr("c", "#00f")
    step(1)
    step(125)
    assert root.getAttribute("c") == interpolate_rgb("#f00", "#00f")(t)


def test_transition_attr_builds_interpolator_after_start_listener() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)

    def on_start(*_args) -> None:
        s.attr("fill", "red")

    s.transition().delay(1).on("start", on_start).attr("fill", lambda *_: "blue")
    step(1)
    step(125)
    t = easeCubicInOut(125 / 250)
    assert root.getAttribute("fill") == interpolate_rgb("red", "blue")(t)


def test_transition_attr_tween_factory_returns_interpolator_like_upstream() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    select(root).attr("fill", "red")
    t = select(root).transition().delay(1).attr("fill", "blue")
    step = _with_virtual_time()
    step(1)
    factory = t.attrTween("fill")
    assert factory is not None
    interp = factory(root)
    assert interp(0.5) == "rgb(128, 0, 128)"


def test_transition_tween_attr_fill_applies_midpoint() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    select(root).attr("fill", "red")
    t = select(root).transition().delay(1).attr("fill", "blue")
    step = _with_virtual_time()
    step(1)
    tick = t.tween("attr.fill")(root)
    assert tick is not None
    tick(root, 0.5)
    assert root.getAttribute("fill") == "rgb(128, 0, 128)"


def test_transition_attr_function_evaluated_midpoint_matches_upstream_colors() -> None:
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
    step = _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    ease = easeCubicInOut
    duration = 250.0
    interp1 = interpolate_rgb("cyan", "red")
    interp2 = interpolate_rgb("magenta", "green")
    result: list[list[object]] = []
    s = selectAll([one, two]).data(["red", "green"])
    s.attr("fill", lambda _this, d, *_args: ("cyan" if d == "red" else "magenta"))

    def value(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])
        return d

    s.transition().attr("fill", value)
    assert result == [
        ["red", 0, [one, two], one],
        ["green", 1, [one, two], two],
    ]
    step(125)
    t = ease(125 / duration)
    assert one.getAttribute("fill") == interp1(t)
    assert two.getAttribute("fill") == interp2(t)


def test_transition_style_font_size_number_leaves_px_when_nan() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).style("font-size", "15px").transition().delay(1).style("font-size", 10)
    step(1)
    step(125)
    assert root.style.getPropertyValue("font-size") == "15px"


def test_transition_style_font_size_function_number_leaves_px_when_nan() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).style("font-size", "15px").transition().delay(1).style("font-size", lambda *_: 10)
    step(1)
    step(125)
    assert root.style.getPropertyValue("font-size") == "15px"


def test_transition_style_function_explicit_none_removes_after_start() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).style("color", "red")
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert root.style.getPropertyValue("color") == "red"

    select(root).transition().delay(1).style("color", lambda *_: None).on("start", on_start)
    step(1)
    assert started["ok"] is True
    step(1)
    assert root.style.getPropertyValue("color") == ""


def test_transition_style_function_noop_when_coerced_matches() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).style("opacity", 1)
    select(root).transition().delay(1).style("opacity", lambda *_: 1)
    step(1)
    step(125)
    root.style.setProperty("opacity", "0.5")
    step(125)
    assert root.style.getPropertyValue("opacity") == "0.5"


def test_transition_tween_style_color_applies_midpoint() -> None:
    g.document = parse_html("<html><body></body></html>")
    root = g.document.documentElement
    select(root).style("color", "red")
    t = select(root).transition().delay(1).style("color", "blue")
    step = _with_virtual_time()
    step(1)
    tick = t.tween("style.color")(root)
    assert tick is not None
    tick(root, 0.5)
    assert root.style.getPropertyValue("color") == "rgb(128, 0, 128)"


def test_transition_style_interpolates_number_string_and_color() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    ease = easeCubicInOut
    duration = 250.0
    t = ease(125 / duration)

    select(root).style("opacity", "0").transition().delay(1).style("opacity", 1)
    step(1)
    step(125)
    assert root.style.getPropertyValue("opacity") == str(interpolate_number(0, 1)(t))

    select(root).style("font-size", "1px").transition().delay(1).style("font-size", "2px")
    step(1)
    step(125)
    assert root.style.getPropertyValue("font-size") == interpolate_string("1px", "2px")(t)

    select(root).style("color", "#f00").transition().delay(1).style("color", "#00f")
    step(1)
    step(125)
    assert root.style.getPropertyValue("color") == interpolate_rgb("#f00", "#00f")(t)


def test_transition_style_tween_color_midpoint_and_priority() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    h = interpolate_hcl("red", "blue")
    select(root).transition().delay(1).styleTween("color", lambda *_: h)
    step(1)
    step(125)
    assert root.style.getPropertyValue("color") == h(easeCubicInOut(125 / 250))
    assert root.style.getPropertyPriority("color") == ""

    select(root).transition().delay(1).styleTween("color", lambda *_: h, "important")
    step(1)
    step(125)
    assert root.style.getPropertyValue("color") == h(easeCubicInOut(125 / 250))
    assert root.style.getPropertyPriority("color") == "important"


def test_transition_attr_function_removes_when_returns_none() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).attr("fill", "red")
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert root.getAttribute("fill") == "red"

    def value(*_args):
        return None

    select(root).transition().delay(1).attr("fill", value).on("start", on_start)
    step(1)
    assert started["ok"] is True
    step(1)
    assert root.hasAttribute("fill") is False


def test_transition_style_function_removes_when_returns_none() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    select(root).style("color", "red")
    started = {"ok": False}

    def on_start(*_args) -> None:
        started["ok"] = True
        assert root.style.getPropertyValue("color") == "red"

    def value(*_args):
        return None

    select(root).transition().delay(1).style("color", value).on("start", on_start)
    step(1)
    assert started["ok"] is True
    step(1)
    assert root.style.getPropertyValue("color") == ""


def test_transition_style_on_start_sets_color_before_interpolator() -> None:
    g.document = parse_html("<html><body></body></html>")
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)

    def on_start(*_args) -> None:
        s.style("color", "red")

    s.transition().delay(1).on("start", on_start).style("color", lambda *_: "blue")
    step(1)
    step(125)
    t = easeCubicInOut(125 / 250)
    assert root.style.getPropertyValue("color") == interpolate_rgb("red", "blue")(t)
