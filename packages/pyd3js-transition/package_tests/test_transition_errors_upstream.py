from __future__ import annotations

import pytest

import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_selection.selection.index import selection


class Node:
    def __init__(self) -> None:
        self.__data__ = None
        self.attrs: dict[str, str] = {}

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


def _with_virtual_time() -> tuple[list[float], callable]:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return wall, step


def test_on_start_error_terminates_transition() -> None:
    _, step = _with_virtual_time()
    n = Node()
    s = selection([[n]], [None])

    s.transition().on("start", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError, match="boom"):
        step(0)
    assert getattr(n, "__transition__", None) is None


def test_on_start_error_with_delay_terminates_transition() -> None:
    _, step = _with_virtual_time()
    n = Node()
    s = selection([[n]], [None])

    s.transition().delay(50).on("start", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError, match="boom"):
        step(50)
    assert getattr(n, "__transition__", None) is None


def test_tween_value_error_terminates_transition() -> None:
    _, step = _with_virtual_time()
    n = Node()
    s = selection([[n]], [None])

    s.transition().tween("foo", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError, match="boom"):
        step(0)
    assert getattr(n, "__transition__", None) is None


def test_tween_value_error_with_delay_terminates_transition() -> None:
    _, step = _with_virtual_time()
    n = Node()
    s = selection([[n]], [None])

    s.transition().delay(50).tween("foo", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError, match="boom"):
        step(50)
    assert getattr(n, "__transition__", None) is None


def test_tween_deferred_error_terminates_transition() -> None:
    _, step = _with_virtual_time()
    n = Node()
    s = selection([[n]], [None])

    def value(*_args):
        def tick(_node, t: float) -> None:
            if t == 1:
                raise RuntimeError("boom")

        return tick

    s.transition().duration(50).tween("foo", value)
    # Start + run to end.
    step(0)
    with pytest.raises(RuntimeError, match="boom"):
        step(60)
    assert getattr(n, "__transition__", None) is None


def test_on_end_error_terminates_transition() -> None:
    _, step = _with_virtual_time()
    n = Node()
    s = selection([[n]], [None])

    s.transition().delay(50).duration(50).on(
        "end",
        lambda *_: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    step(50)  # start
    with pytest.raises(RuntimeError, match="boom"):
        step(60)  # end
    assert getattr(n, "__transition__", None) is None

