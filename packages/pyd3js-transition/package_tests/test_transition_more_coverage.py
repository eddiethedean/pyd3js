from __future__ import annotations

from typing import Any, Callable

import pytest

import pyd3js_timer._engine as timer_engine
from pyd3js_selection.selection.index import selection
from pyd3js_transition import interrupt
from pyd3js_transition.selection.interrupt import selection_interrupt
from pyd3js_transition.selection.transition import selection_transition
from pyd3js_transition.transition import attr as attrmod
from pyd3js_transition.transition import schedule as sch
from pyd3js_transition.transition import style as stylemod
from pyd3js_transition.transition.tween import _call_value as tween_call_value


class Node:
    def __init__(self, parent: Any | None = None) -> None:
        self.parentNode = parent
        self.__data__ = {"x": 1}
        self.attrs: dict[str, str] = {}
        self.style: dict[str, str] = {}
        self.textContent = ""

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


def _with_virtual_time() -> tuple[list[float], Callable[[float], None]]:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return wall, step


def test_tween_call_value_arity_fallbacks() -> None:
    assert tween_call_value(lambda this, d, i, nodes: (this, d, i, nodes), 1, 2, 3, [4]) == (1, 2, 3, [4])
    assert tween_call_value(lambda d, i, nodes: (d, i, nodes), 1, 2, 3, [4]) == (2, 3, [4])
    assert tween_call_value(lambda d, i: (d, i), 1, 2, 3, [4]) == (2, 3)
    assert tween_call_value(lambda this: this, 1, 2, 3, [4]) == 1
    # One-arg callback receives `this` in our port (mirrors selection semantics).
    assert tween_call_value(lambda d: d, 1, 2, 3, [4]) == 1
    assert tween_call_value(lambda: 9, 1, 2, 3, [4]) == 9


def test_selection_interrupt_calls_interrupt() -> None:
    n = Node()
    s = selection([[n]], [None])
    s.transition("x")  # create schedule
    selection_interrupt(s, "x")
    assert getattr(n, "__transition__", None) is None


def test_selection_transition_inherit_from_parent() -> None:
    wall, step = _with_virtual_time()
    parent = Node()
    child = Node(parent=parent)
    s = selection([[parent]], [None])
    t = s.transition("x").duration(100)
    # schedule exists on parent; inherit should find it from child.parentNode
    t2 = selection([[child]], [None]).transition(t)
    assert t2._id == t._id
    step(50)


def test_schedule_skips_duplicate_id() -> None:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()
    n = Node()
    t = selection([[n]], [None]).transition("x")
    before = dict(getattr(n, "__transition__", {}))
    sch.schedule(n, "x", t._id, 0, [n], {"time": wall[0], "delay": 0, "duration": 10, "ease": lambda x: x})
    after = dict(getattr(n, "__transition__", {}))
    assert before.keys() == after.keys()


def test_init_too_late_error() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    t = selection([[n]], [None]).transition("x")
    step(50)
    with pytest.raises(RuntimeError):
        sch.init(n, t._id)


def test_interrupt_other_name_sets_empty_false_path() -> None:
    n = Node()
    selection([[n]], [None]).transition("x")
    interrupt(n, "y")
    assert getattr(n, "__transition__", None) is not None


def test_attr_constant_and_remove_paths() -> None:
    n = Node()
    _wall, step = _with_virtual_time()
    selection([[n]], [None]).transition("x").duration(10).attr("a", "b")
    step(50)
    assert n.getAttribute("a") == "b"


def test_attr_function_path_removes_when_none() -> None:
    n = Node()
    n.setAttribute("a", "1")

    def val(this: Any) -> Any:
        return None

    _wall, step = _with_virtual_time()
    selection([[n]], [None]).transition("x").duration(10).attr("a", val)
    step(50)
    assert n.getAttribute("a") is None


def test_style_constant_and_remove_paths() -> None:
    n = Node()
    _wall, step = _with_virtual_time()
    selection([[n]], [None]).transition("x").duration(10).style("fill", "red")
    step(50)
    assert n.style.get("fill") == "red"
    # null style path
    selection([[n]], [None]).transition("y").duration(10).style("fill", None)

