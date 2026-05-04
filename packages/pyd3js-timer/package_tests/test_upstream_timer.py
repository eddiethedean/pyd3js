"""Port of d3-timer ``test/timer-test.js``."""

from __future__ import annotations

import time

import pytest

import pyd3js_timer._engine as eng
from pyd3js_timer import Timer, now, timer, timer_flush

from upstream_support import assert_in_range, idle_ms


def test_timer_callback_returns_timer_instance() -> None:
    t = timer(lambda _e: None)
    assert isinstance(t, Timer)
    t.stop()


def test_timer_callback_requires_function() -> None:
    with pytest.raises(TypeError):
        timer()  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        timer("42")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        timer(None)  # type: ignore[arg-type]


def test_timer_invokes_about_every_17ms() -> None:
    then = now()
    count = [0]
    done: list[bool] = []

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] > 10:
            t_holder[0].stop()
            assert_in_range(now() - then, (17.0 - 5.0) * count[0], (17.0 + 5.0) * count[0])
            done.append(True)

    t_holder: list = [timer(cb)]
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_invokes_until_stopped() -> None:
    count = [0]
    done: list[bool] = []

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] > 2:
            t_holder[0].stop()
            done.append(True)

    t_holder: list = [timer(cb)]
    deadline = time.monotonic() + 4.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


@pytest.mark.skip(reason="Python has no JS `this` binding for plain callbacks.")
def test_timer_uses_undefined_context() -> None:
    timer(lambda _e: None)


def test_timer_passes_elapsed_time() -> None:
    then = now()
    count = [0]
    done: list[bool] = []

    def cb(elapsed: float) -> None:
        count[0] += 1
        assert elapsed == now() - then
        if count[0] > 10:
            t_holder[0].stop()
            done.append(True)

    t_holder: list = [timer(cb)]
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_delay_first_invoke_after_delay() -> None:
    then = now()
    delay = 150.0
    done: list[bool] = []

    def cb(_e: float) -> None:
        t_holder[0].stop()
        assert_in_range(now() - then, delay - 25.0, delay + 25.0)
        done.append(True)

    t_holder: list = [timer(cb, delay)]
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_delay_elapsed_relative_to_delay() -> None:
    delay = 150.0
    done: list[bool] = []

    def cb(elapsed: float) -> None:
        t_holder[0].stop()
        assert_in_range(elapsed, 0.0, 20.0)
        done.append(True)

    t_holder: list = [timer(cb, delay)]
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_delay_time_effective_skew() -> None:
    delay = 150.0
    skew = 200.0
    done: list[bool] = []

    def cb(elapsed: float) -> None:
        t_holder[0].stop()
        assert_in_range(elapsed, skew - delay + 17.0 - 15.0, skew - delay + 17.0 + 15.0)
        done.append(True)

    t_holder: list = [timer(cb, delay, now() - skew)]
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_scheduling_order_synchronous_flush() -> None:
    results: list[int] = []
    t0 = timer(lambda _e: (results.append(1), t0.stop()))
    t1 = timer(lambda _e: (results.append(2), t1.stop()))
    t2 = timer(lambda _e: (results.append(3), t2.stop()))
    timer_flush()
    assert results == [1, 2, 3]


def test_timer_scheduling_order_asynchronous_flush() -> None:
    results: list[int] = []
    done: list[bool] = []

    def check(_e: float) -> None:
        t3.stop()
        assert results == [1, 2, 3]
        done.append(True)

    t0 = timer(lambda _e: (results.append(1), t0.stop()))
    t1 = timer(lambda _e: (results.append(2), t1.stop()))
    t2 = timer(lambda _e: (results.append(3), t2.stop()))
    t3 = timer(check)
    deadline = time.monotonic() + 3.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_different_delays_async_scheduling_order() -> None:
    """All timers share one anchor time; advance wall so every timer is due in one ``timer_flush``."""
    wall = [0.0]
    eng._set_wall_ms_factory(lambda: wall[0])
    eng._reset_for_tests()
    try:
        then = now()
        results_holder: list[list[int] | None] = [None]
        t_hold: list[Timer | None] = [None, None, None, None]

        def t0_cb(_e: float) -> None:
            results_holder[0] = [1]
            assert t_hold[0] is not None
            t_hold[0].stop()

        def t1_cb(_e: float) -> None:
            if results_holder[0] is not None:
                results_holder[0].append(2)
            assert t_hold[1] is not None
            t_hold[1].stop()

        def t2_cb(_e: float) -> None:
            if results_holder[0] is not None:
                results_holder[0].append(3)
            assert t_hold[2] is not None
            t_hold[2].stop()

        def t3_cb(_e: float) -> None:
            assert t_hold[3] is not None
            t_hold[3].stop()
            assert results_holder[0] == [1, 2, 3]

        t_hold[0] = timer(t0_cb, 60, then)
        t_hold[1] = timer(t1_cb, 40, then)
        t_hold[2] = timer(t2_cb, 80, then)
        t_hold[3] = timer(t3_cb, 100, then)
        wall[0] = float(then) + 150.0
        timer_flush()
    finally:
        eng._set_wall_ms_factory(None)
        eng._reset_for_tests()


def test_timer_within_frame_inner_zero_elapsed() -> None:
    """Inner timer is scheduled during outer callback; same ``timer_flush`` visits it (d3 ordering)."""
    then = now()
    inner_holder: list[Timer | None] = [None]
    outer_holder: list[Timer | None] = [None]

    def outer(_e: float, *_args: object) -> None:
        delay = now() - then

        def inner(elapsed2: float, *_a2: object) -> None:
            assert inner_holder[0] is not None
            inner_holder[0].stop()
            assert elapsed2 == 0.0
            assert_in_range(now() - then, delay, delay + 8.0)

        inner_holder[0] = timer(inner, 0, now())
        assert outer_holder[0] is not None
        outer_holder[0].stop()

    outer_holder[0] = timer(outer)
    timer_flush()


@pytest.mark.skip(
    reason=(
        "d3 Mocha counts global setTimeout calls; Python uses threading.Timer for "
        "frames, wakes, and poke—trace semantics do not match 1:1."
    )
)
def test_timer_delay_within_timerflush_no_duplicate_frames() -> None:
    """Port of timer-test duplicate-frame assertion (Node ``setTimeout`` hook)."""


@pytest.mark.skip(
    reason=(
        "d3 Mocha counts global setTimeout calls; Python scheduling trace differs "
        "under threading."
    )
)
def test_timer_switches_to_long_wake_for_long_delays() -> None:
    """Port of timer-test long-delay / short-delay frame split (Node hook)."""


def test_timer_stop_immediately_stops_after_brief_delay() -> None:
    count = [0]
    t = timer(lambda _e: count.__setitem__(0, count[0] + 1))
    idle_ms(24)
    t.stop()
    assert count[0] == 1


@pytest.mark.skip(
    reason=(
        "Upstream asserts exact ``setTimeout`` delay sequence; threaded wakes append "
        "many frame traces—use ``test_sleep_cancels_pending_long_timeout`` for wake cancel."
    )
)
def test_timer_stop_recomputes_wake_after_frame() -> None:
    """Port of timer-test ``timer.stop() recomputes the new wake time after one frame``."""


def test_timer_restart_requires_function() -> None:
    t = timer(lambda _e: None)
    with pytest.raises(TypeError):
        t.restart()  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        t.restart(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        t.restart("42")  # type: ignore[arg-type]
    t.stop()


def test_timer_restart_implicit_zero_delay() -> None:
    done: list[bool] = []

    def on_restart(elapsed: float) -> None:
        assert_in_range(elapsed, 17.0 - 15.0, 17.0 + 15.0)
        t_holder[0].stop()
        done.append(True)

    t_holder: list[Timer] = [timer(lambda _e: None, 1000)]
    t_holder[0].restart(on_restart)
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


@pytest.mark.skip(
    reason="Same delay-sequence assertion as ``test_timer_stop_recomputes_wake_after_frame`` (Node hook)."
)
def test_timer_restart_delay_time_recomputes_wake() -> None:
    """Port of timer-test ``timer.restart(callback, delay, time) recomputes…``."""


def test_timer_stop_then_restart_no_infinite_loop() -> None:
    t = timer(lambda _e: None)
    last: list[float | None] = [None]

    def on_restart(elapsed: float) -> None:
        if last[0] is None:
            last[0] = elapsed
            return
        if elapsed == last[0]:
            pytest.fail("repeated invocation")
        t.stop()

    t.stop()
    t.restart(on_restart)


def test_timer_stop_then_restart_no_infinite_loop_two_timers() -> None:
    t0 = timer(lambda _e: None)
    t1 = timer(lambda _e: None)
    last: list[float | None] = [None]

    def on_restart(elapsed: float) -> None:
        if last[0] is None:
            last[0] = elapsed
            return
        if elapsed == last[0]:
            pytest.fail("repeated invocation")
        t0.stop()

    t0.stop()
    t0.restart(on_restart)
    t1.stop()


def test_timer_stop_clears_next_after_timeout() -> None:
    t0 = timer(lambda _e: None)
    t1 = timer(lambda _e: None)
    t0.stop()
    idle_ms(100)
    assert t0._next is None
    t1.stop()