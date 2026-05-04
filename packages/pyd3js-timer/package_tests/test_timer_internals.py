from __future__ import annotations

import time

import pyd3js_timer._engine as tim
from pyd3js_timer import IntervalTimer


def test_interval_timer_restart_with_none_delay_delegates() -> None:
    it = IntervalTimer()
    it.restart(lambda _e: None, None, None)
    it.stop()


def test_nap_prunes_stopped_head_with_manual_chain() -> None:
    """``_nap`` must splice out a stopped head when a live node follows."""
    tim._reset_for_tests()
    dead = tim.Timer()
    alive = tim.Timer()
    dead._call = None
    dead._time = float("inf")
    dead._next = alive
    alive._call = lambda _e: None
    alive._time = 0.0
    alive._next = None
    tim._task_head = dead
    tim._task_tail = alive
    tim._nap()
    assert tim._task_head is alive
    assert tim._task_tail is alive
    alive.stop()
    tim._nap()


def test_nap_prunes_stopped_middle_node() -> None:
    tim._reset_for_tests()
    a = tim.Timer()
    d = tim.Timer()
    c = tim.Timer()
    a._call = lambda _e: None
    a._time = 0.0
    d._call = None
    d._time = float("inf")
    c._call = lambda _e: None
    c._time = 0.0
    a._next = d
    d._next = c
    c._next = None
    tim._task_head = a
    tim._task_tail = c
    tim._nap()
    assert tim._task_head is a
    assert a._next is c
    a.stop()
    c.stop()
    tim._nap()


def test_sleep_cancels_pending_long_timeout() -> None:
    """When a short-delay timer is scheduled, a pending long wake is cancelled."""
    tim._reset_for_tests()
    tim.timer(lambda _e: None, 10_000)
    time.sleep(0.1)
    assert tim._timeout_flag == 1
    tim.timer(lambda _e: None, 1)
    assert tim._timeout_flag == 0
    tim._reset_for_tests()


def test_poke_adjusts_skew_when_wall_jumps() -> None:
    tim._reset_for_tests()
    wall = [0.0]
    tim._set_wall_ms_factory(lambda: wall[0])
    with tim._lock:
        tim._clock_last = 0.0
    wall[0] = 2000.0
    tim._poke()
    tim._reset_for_tests()


def test_schedule_next_poke_iteration() -> None:
    tim._reset_for_tests()
    tim._poke_delay_ms = 0.05
    seen: list[int] = []

    def chain() -> None:
        seen.append(1)
        with tim._lock:
            tim._interval_flag = 0

    with tim._lock:
        tim._interval_flag = 1
    tim._schedule_next_poke_iteration(chain)
    time.sleep(0.12)
    assert seen == [1]
    tim._reset_for_tests()


def test_poke_chain_step_runs_synchronously() -> None:
    tim._reset_for_tests()
    with tim._lock:
        tim._interval_flag = 1
    tim._create_poke_chain()()
    tim._cancel_timer(tim._poke_timer)
    with tim._lock:
        tim._poke_timer = None
        tim._interval_flag = 0
    tim._reset_for_tests()


def test_trace_schedule_ms_records_when_recorder_set() -> None:
    """Cover ``_trace_schedule_ms`` append path (used by skipped Node parity tests)."""
    tim._reset_for_tests()
    rec: list[float] = []
    tim._test_scheduled_delays_ms = rec
    try:
        tim._set_frame(lambda: None)
        assert len(rec) >= 1
        assert abs(rec[-1] - tim.FRAME_MS) < 0.01
    finally:
        tim._cancel_timer(tim._frame_timer)
        tim._frame_timer = None
        tim._test_scheduled_delays_ms = None
        tim._reset_for_tests()


def test_schedule_next_poke_iteration_skips_when_inactive() -> None:
    tim._reset_for_tests()
    with tim._lock:
        tim._interval_flag = 0
    tim._schedule_next_poke_iteration(lambda: None)
    assert tim._poke_timer is None
    tim._reset_for_tests()
