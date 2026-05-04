from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import pyd3js_timer._engine as timer_engine
import pyd3js_transition as tr
from pyd3js_selection.selection.index import selection
from pyd3js_transition.transition import schedule as sch
from pyd3js_transition.transition._style import style_remove, style_set, style_value
from pyd3js_transition.transition.interpolate import interpolate


class Node:
    def __init__(self, parent: Any | None = None) -> None:
        self.parentNode = parent
        self.__data__ = None
        self.attrs: dict[str, str] = {}
        self.style: dict[str, str] = {}
        self.textContent = ""

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


def _step(ms: float) -> None:
    """Advance virtual wall clock and flush due timers."""
    wall[0] += ms
    timer_engine.timer_flush()
    timer_engine.timer_flush()


wall = [0.0]


@pytest.fixture(autouse=True)
def _virtual_time() -> None:
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()
    wall[0] = 0.0
    yield
    timer_engine._set_wall_ms_factory(None)
    timer_engine._reset_for_tests()


def test_style_helpers_dict() -> None:
    n = Node()
    assert style_value(n, "fill") is None
    style_set(n, "fill", "red")
    assert style_value(n, "fill") == "red"
    style_remove(n, "fill")
    assert style_value(n, "fill") is None


def test_style_helpers_object_with_methods() -> None:
    calls: list[tuple[str, str, str]] = []

    class StyleObj:
        def setProperty(self, name: str, value: str, priority: str) -> None:  # noqa: N802
            calls.append(("set", name, value))

        def removeProperty(self, name: str) -> None:  # noqa: N802
            calls.append(("rm", name, ""))

    node = SimpleNamespace(style=StyleObj())
    style_set(node, "opacity", 0.5, "important")
    style_remove(node, "opacity")
    assert calls[0][:2] == ("set", "opacity")
    assert calls[1][:2] == ("rm", "opacity")


def test_interpolate_number_color_string_paths() -> None:
    f = interpolate(None, 10)
    assert f(1.0) == 10.0
    g = interpolate("red", "blue")
    assert isinstance(g(0.5), str)
    h = interpolate("a", "b")
    assert isinstance(h(0.0), str)


def test_active_none_and_non_none() -> None:
    n = Node()
    assert tr.active(n, "x") is None
    s = selection([[n]], [None])
    t = s.transition("x")
    t.on("end._t", lambda *_: None)
    # advance enough to be > SCHEDULED
    _step(50)
    a = tr.active(n, "x")
    assert a is not None
    assert a._name == "x"


def test_interrupt_empty_and_other_name() -> None:
    n = Node()
    tr.interrupt(n, "x")  # no schedules
    s = selection([[n]], [None])
    s.transition("x")
    tr.interrupt(n, "y")  # leaves schedule, marks empty False
    assert getattr(n, "__transition__", None) is not None


def test_interrupt_cancels_and_clears() -> None:
    n = Node()
    s = selection([[n]], [None])
    s.transition("x")
    tr.interrupt(n, "x")
    assert getattr(n, "__transition__", None) is None


def test_schedule_get_init_set_errors() -> None:
    n = Node()
    with pytest.raises(RuntimeError):
        sch.get(n, 1)
    t = selection([[n]], [None]).transition("x").duration(1000)
    _ = sch.init(n, t._id)
    _ = sch.set(n, t._id)
    _step(200)  # ensure first tick runs -> RUNNING
    with pytest.raises(RuntimeError):
        sch.set(n, t._id)


def test_transition_tween_get_set_remove() -> None:
    n = Node()
    t = selection([[n]], [None]).transition("x")

    assert t.tween("k") is None
    t.tween("k", lambda this, *_: (lambda _t: None))
    assert callable(t.tween("k"))
    t.tween("k", None)
    assert t.tween("k") is None


def test_delay_duration_ease_get_set() -> None:
    n = Node()
    t = selection([[n]], [None]).transition("x")
    assert t.delay() == 0.0
    t.delay(5)
    assert t.delay() == 5.0
    assert t.duration() == 250.0
    t.duration(10)
    assert t.duration() == 10.0
    t.ease(lambda x: x)
    assert t.ease()(0.5) == 0.5


def test_ease_varying() -> None:
    n = Node()
    t = selection([[n]], [None]).transition("x")
    t.easeVarying(lambda *_: (lambda x: x * 0.0))
    assert t.ease()(0.2) == 0.0

