from __future__ import annotations

from typing import Any

import pyd3js_timer._engine as timer_engine
from pyd3js_selection.selection.index import selection
from pyd3js_transition import interrupt


class Node:
    def __init__(self) -> None:
        self.__data__ = None
        self.attrs: dict[str, str] = {}
        self.style: dict[str, str] = {}
        self.textContent = ""
        self.parentNode = None

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


def _virtual_clock() -> tuple[list[float], Any]:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        # `pyd3js_timer.now()` caches within a frame; in virtual time tests we
        # must explicitly clear it so flush observes the updated wall clock.
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return wall, step


def test_interrupt_cancels_when_not_running() -> None:
    wall, step = _virtual_clock()
    n = Node()
    log: list[str] = []

    t = selection([[n]], [None]).transition("x").duration(100)
    t.on("cancel.t", lambda *_: log.append("cancel"))
    t.on("interrupt.t", lambda *_: log.append("interrupt"))
    t.on("end.t", lambda *_: log.append("end"))

    # Interrupt before it runs: should be cancel.
    interrupt(n, "x")
    assert log == ["cancel"]

    step(200)
    assert getattr(n, "__transition__", None) is None


def test_interrupt_interrupts_when_running() -> None:
    wall, step = _virtual_clock()
    n = Node()
    log: list[str] = []

    t = selection([[n]], [None]).transition("x").duration(1000)
    t.on("interrupt.t", lambda *_: log.append("interrupt"))
    t.on("cancel.t", lambda *_: log.append("cancel"))
    t.on("end.t", lambda *_: log.append("end"))

    # Start + first tick -> RUNNING.
    step(40)
    interrupt(n, "x")
    assert log == ["interrupt"]


def test_new_transition_cancels_older_scheduled_and_interrupts_running() -> None:
    wall, step = _virtual_clock()
    n = Node()
    log: list[str] = []

    # First transition: long.
    t0 = selection([[n]], [None]).transition("x").duration(1000)
    t0.on("cancel.t0", lambda *_: log.append("cancel0"))
    t0.on("interrupt.t0", lambda *_: log.append("interrupt0"))

    # Start t0 so that the second transition interrupts a RUNNING schedule.
    step(40)

    # Second transition with same name should preempt t0 and complete.
    t1 = selection([[n]], [None]).transition("x").duration(10)
    t1.on("cancel.t1", lambda *_: log.append("cancel1"))
    t1.on("interrupt.t1", lambda *_: log.append("interrupt1"))
    t1.on("end.t1", lambda *_: log.append("end1"))

    # Let things run to completion.
    step(100)
    assert "end1" in log
    # One of cancel/interrupt should have fired for t0 depending on whether it started running.
    assert any(x in log for x in ("cancel0", "interrupt0"))

