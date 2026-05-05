"""Targeted tests for remaining line-coverage gaps (drive toward 100%)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
import pyd3js_selection._globals as g
import pyd3js_timer._engine as timer_engine
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
from pyd3js_selection.selection.index import selection

import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition.transition import schedule as sched
from pyd3js_transition.transition._style import style_value
from pyd3js_transition.transition.attr import (
    _attr_function,
    _attr_function_ns,
    _attr_remove_ns,
    _remove_attr_ns,
)
from pyd3js_transition.transition.interpolate import interpolate
from pyd3js_transition.transition.style import _style_null


class Node:
    def __init__(self, parent: Any | None = None) -> None:
        self.parentNode = parent
        self.__data__ = {}
        self.attrs: dict[str, str] = {}
        self.style: dict[str, str] = {}
        self.textContent = ""

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


def _with_virtual_time() -> Any:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return wall, step


def test_style_value_falls_through_when_style_object_lacks_get_property_value() -> None:
    class El:
        style = SimpleNamespace()

    assert style_value(El(), "opacity") is None


def test_style_null_memo_second_invocation() -> None:
    n = Node()
    n.style["fill"] = "red"
    fn = _style_null("fill", interpolate)
    r1 = fn(n)
    assert r1 is not None
    n.style["fill"] = "red"
    r2 = fn(n)
    assert r2 is r1


def test_style_null_no_interpolation_when_before_after_remove_match() -> None:
    n = Node()
    fn = _style_null("ghost", interpolate)
    assert fn(n) is None


def test_remove_attr_ns_on_element_object() -> None:
    class NsEl(Node):
        def removeAttributeNS(self, space: str, local: str) -> None:  # noqa: N802
            self.attrs.pop(f"{space}|{local}", None)

    el = NsEl()
    el.attrs["http://x|y"] = "1"
    _remove_attr_ns(el, "http://x", "y")
    assert "http://x|y" not in el.attrs


def test_attr_remove_ns_lambda_invokes_remove() -> None:
    rm = _attr_remove_ns({"space": "http://x", "local": "y"})
    hits: list[Any] = []

    class E:
        def removeAttributeNS(self, space: str, local: str) -> None:
            hits.append((space, local))

    rm(E())
    assert hits == [("http://x", "y")]


def test_attr_function_noop_when_current_equals_target() -> None:
    n = Node()
    n.attrs["k"] = "same"
    fn = _attr_function("k", interpolate, lambda _this: "same")
    assert fn(n) is None


def test_attr_function_ns_noop_when_current_equals_target() -> None:
    uri = "http://www.w3.org/2000/svg"
    n = Node()
    n.attrs[f"{uri}|fill"] = "blue"

    def _get(space: str, local: str) -> str | None:
        return n.attrs.get(f"{space}|{local}")

    n.getAttributeNS = _get  # type: ignore[method-assign]

    fn = _attr_function_ns({"space": uri, "local": "fill"}, interpolate, lambda _this: "blue")
    assert fn(n) is None


def test_attr_function_ns_returns_memo_on_second_invocation() -> None:
    uri = "http://www.w3.org/2000/svg"
    n = Node()
    n.attrs[f"{uri}|fill"] = "red"

    def _get(space: str, local: str) -> str | None:
        return n.attrs.get(f"{space}|{local}")

    n.getAttributeNS = _get  # type: ignore[method-assign]

    fn = _attr_function_ns({"space": uri, "local": "fill"}, interpolate, lambda _this: "blue")
    a = fn(n)
    assert a is not None
    assert fn(n) is a


def test_transition_namespaced_attr_finalize_sets_attribute_ns() -> None:
    g.document = parse_html("<html><body></body></html>")
    _wall, step = _with_virtual_time()
    root = g.document.documentElement
    uri = "http://www.w3.org/2000/svg"
    select(root).attr("svg:fill", "red")
    select(root).transition().duration(10).attr("svg:fill", "blue")
    step(1)
    step(250)
    assert root.getAttributeNS(uri, "fill") == "blue"


def test_defer_start_retry_calls_timeout_with_start_closure() -> None:
    log: list[Any] = []

    def timeout_fn(fn: Any, delay: Any) -> None:
        log.append(("timeout", delay))
        fn(0)

    def start_fn(elapsed: float) -> None:
        log.append(("start", elapsed))

    sched._defer_start_retry(timeout_fn, start_fn, 7.5, 3.0)
    assert ("timeout", 3.0) in log
    assert ("start", 7.5) in log


def test_tick_skip_idle_state_matches_schedule_tick_guard() -> None:
    assert sched._tick_skip_idle_state(sched.ENDED)
    assert sched._tick_skip_idle_state(sched.CREATED)
    assert not sched._tick_skip_idle_state(sched.STARTED)
    assert not sched._tick_skip_idle_state(sched.RUNNING)
    assert not sched._tick_skip_idle_state(sched.ENDING)


def test_tick_early_return_after_interrupt_during_tween() -> None:
    """Interrupt ends transition; remaining work should not assume RUNNING."""
    from pyd3js_transition import interrupt

    _wall, step = _with_virtual_time()
    n = Node()
    hits: list[float] = []

    def factory(_node: Any, _d: Any, _i: int, _grp: list[Any]):
        def interp(this: Any, t: float) -> None:
            hits.append(t)
            if t >= 0.3:
                interrupt(this, "tic")

        return interp

    selection([[n]], [None]).transition("tic").duration(15).tween("z", factory)
    step(50)


def test_namespaced_attr_removed_via_public_api() -> None:
    g.document = parse_html("<html><body></body></html>")
    _wall, step = _with_virtual_time()
    root = g.document.documentElement
    uri = "http://www.w3.org/2000/svg"
    select(root).attr("svg:fill", "red")
    select(root).transition().duration(5).attr("svg:fill", None)
    step(10)
    assert root.getAttributeNS(uri, "fill") is None
