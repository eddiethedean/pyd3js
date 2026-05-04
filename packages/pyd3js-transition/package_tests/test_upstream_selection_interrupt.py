from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_selection._dom import Document
from pyd3js_selection.select import select
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


def _set_document() -> None:
    g.document = Document()


def test_selection_interrupt_returns_selection() -> None:
    _set_document()
    s = select(g.document)
    assert s.interrupt() is s


def test_selection_interrupt_cancels_pending_transitions() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition()
    t2 = t1.transition()
    assert t1._id in root.__transition__
    assert t2._id in root.__transition__
    assert s.interrupt() is s
    assert getattr(root, "__transition__", None) is None


def test_selection_interrupt_only_cancels_null_named_by_default() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition("foo")
    t2 = s.transition()
    assert t1._id in root.__transition__
    assert t2._id in root.__transition__
    s.interrupt()
    assert t1._id in root.__transition__
    assert t2._id not in root.__transition__


def test_selection_interrupt_only_cancels_null_named_for_none() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition("foo")
    t2 = s.transition()
    s.interrupt(None)
    assert t1._id in root.__transition__
    assert t2._id not in root.__transition__


def test_selection_interrupt_name_only_cancels_that_name() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition("foo")
    t2 = s.transition()
    s.interrupt("foo")
    assert t1._id not in root.__transition__
    assert t2._id in root.__transition__


def test_selection_interrupt_name_coerces_to_string() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    t1 = s.transition("foo")
    t2 = s.transition()

    class Name:
        def __str__(self) -> str:
            return "foo"

    s.interrupt(Name())
    assert t1._id not in root.__transition__
    assert t2._id in root.__transition__


def test_selection_interrupt_does_nothing_if_no_transition() -> None:
    _set_document()
    root = g.document.documentElement
    s = select(root)
    assert getattr(root, "__transition__", None) is None
    s.interrupt()
    assert getattr(root, "__transition__", None) is None


def test_selection_interrupt_dispatches_interrupt_event_to_started_or_running_transition() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    interrupts = {"n": 0}
    t = s.transition().on("interrupt", lambda *_: interrupts.__setitem__("n", interrupts["n"] + 1))
    schedule = root.__transition__[t._id]

    step(0)  # start frame
    assert schedule["state"] in (sched.STARTED, sched.RUNNING)
    s.interrupt()
    assert schedule["timer"]._call is None
    assert schedule["state"] == sched.ENDED
    assert getattr(root, "__transition__", None) is None
    assert interrupts["n"] == 1


def test_selection_interrupt_destroys_schedule_after_interrupt_dispatch() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)

    t = s.transition()

    def interrupted(*_args) -> None:
        # should still be able to inspect through the API during callback
        assert t.delay() == 0
        assert t.duration() == 250
        assert t.on("interrupt") is interrupted

    t.on("interrupt", interrupted)
    step(0)
    s.interrupt()
    assert getattr(root, "__transition__", None) is None


def test_selection_interrupt_does_not_dispatch_interrupt_for_starting_transition() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    interrupts = {"n": 0}

    t = s.transition().on("interrupt", lambda *_: interrupts.__setitem__("n", interrupts["n"] + 1))
    schedule = root.__transition__[t._id]

    def on_start(*_args) -> None:
        assert schedule["state"] == sched.STARTING
        s.interrupt()
        assert schedule["timer"]._call is None
        assert schedule["state"] == sched.ENDED
        assert getattr(root, "__transition__", None) is None

    t.on("start", on_start)
    step(0)
    assert interrupts["n"] == 0


def test_selection_interrupt_prevents_created_transition_from_starting() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    starts = {"n": 0}
    t = s.transition().on("start", lambda *_: starts.__setitem__("n", starts["n"] + 1))
    schedule = root.__transition__[t._id]
    assert schedule["state"] == sched.CREATED
    s.interrupt()
    assert schedule["timer"]._call is None
    assert schedule["state"] == sched.ENDED
    assert getattr(root, "__transition__", None) is None
    step(10)
    assert starts["n"] == 0


def test_selection_interrupt_prevents_scheduled_transition_from_starting() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    starts = {"n": 0}
    t = s.transition().delay(50).on("start", lambda *_: starts.__setitem__("n", starts["n"] + 1))
    schedule = root.__transition__[t._id]
    step(0)
    assert schedule["state"] == sched.SCHEDULED
    s.interrupt()
    assert schedule["timer"]._call is None
    assert schedule["state"] == sched.ENDED
    assert getattr(root, "__transition__", None) is None
    step(60)
    assert starts["n"] == 0


def test_selection_interrupt_prevents_starting_transition_from_initializing_tweens() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    tweens = {"n": 0}

    def make_tween(*_args):
        tweens["n"] += 1
        return lambda *_: None

    t = s.transition().tween("tween", make_tween)
    schedule = root.__transition__[t._id]

    def on_start(*_args) -> None:
        assert schedule["state"] == sched.STARTING
        s.interrupt()

    t.on("start", on_start)
    step(0)
    step(10)
    assert tweens["n"] == 0


def test_selection_interrupt_during_tween_init_prevents_continuing() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    tweens = {"n": 0}

    def value(*_args):
        s.interrupt()

        def tick(_node, _t: float) -> None:
            tweens["n"] += 1

        return tick

    t = s.transition().tween("tween", value)
    schedule = root.__transition__[t._id]
    step(0)
    step(10)
    assert schedule["timer"]._call is None
    assert schedule["state"] == sched.ENDED
    assert getattr(root, "__transition__", None) is None
    assert tweens["n"] == 0


def test_selection_interrupt_prevents_active_transition_from_continuing() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    interrupted = {"flag": False}
    tweens = {"n": 0}

    def value(*_args):
        def tick(_node, _t: float) -> None:
            if interrupted["flag"]:
                tweens["n"] += 1

        return tick

    t = s.transition().tween("tween", value)
    schedule = root.__transition__[t._id]

    step(0)
    interrupted["flag"] = True
    s.interrupt()
    assert schedule["timer"]._call is None
    assert schedule["state"] == sched.ENDED
    assert getattr(root, "__transition__", None) is None
    step(50)
    assert tweens["n"] == 0


def test_selection_interrupt_during_final_tween_prevents_end_event() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    ends = {"n": 0}

    def value(*_args):
        def tick(_node, t: float) -> None:
            if t >= 1:
                assert root.__transition__[tr._id]["state"] == sched.ENDING
                s.interrupt()

        return tick

    tr = s.transition().duration(50).tween("tween", value).on("end", lambda *_: ends.__setitem__("n", ends["n"] + 1))
    step(0)
    step(60)
    assert getattr(root, "__transition__", None) is None
    assert ends["n"] == 0


def test_selection_interrupt_has_no_effect_on_ended_transition() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    t = s.transition().duration(50)
    schedule = root.__transition__[t._id]
    step(0)
    step(60)
    assert schedule["state"] == sched.ENDED
    assert schedule["timer"]._call is None
    s.interrupt()
    assert schedule["state"] == sched.ENDED
    assert schedule["timer"]._call is None
    assert getattr(root, "__transition__", None) is None


def test_selection_interrupt_has_no_effect_on_interrupting_transition() -> None:
    _set_document()
    step = _with_virtual_time()
    root = g.document.documentElement
    s = select(root)
    interrupts = {"n": 0}

    def interrupted(*_args) -> None:
        interrupts["n"] += 1
        s.interrupt()

    t = s.transition().duration(50).on("interrupt", interrupted)
    schedule = root.__transition__[t._id]
    step(0)
    assert schedule["state"] in (sched.STARTED, sched.RUNNING)
    s.interrupt()
    assert schedule["state"] == sched.ENDED
    assert schedule["timer"]._call is None
    assert interrupts["n"] == 1

