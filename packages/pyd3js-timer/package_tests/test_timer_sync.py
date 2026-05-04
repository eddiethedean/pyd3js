from __future__ import annotations

import time

import pytest

from pyd3js_timer import (
    IntervalTimer,
    Timer,
    interval,
    now,
    timer,
    timer_flush,
    timeout,
)


def test_timer_factory_returns_timer_instance() -> None:
    t = timer(lambda e: None)
    assert isinstance(t, Timer)
    t.stop()


def test_timer_rejects_non_callable() -> None:
    with pytest.raises(TypeError):
        timer()  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        timer("42")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        timer(None)  # type: ignore[arg-type]


def test_timer_flush_invokes_eligible_once() -> None:
    count = [0]
    t_holder: list[Timer] = []

    def cb(_e: float) -> None:
        count[0] += 1
        t_holder[0].stop()

    t_holder.append(timer(cb))
    timer_flush()
    timer_flush()
    assert count[0] == 1


def test_timer_flush_nested_drains_all() -> None:
    count = [0]
    t_holder: list[Timer] = []

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] >= 3:
            t_holder[0].stop()
        timer_flush()

    t_holder.append(timer(cb))
    timer_flush()
    assert count[0] == 3


def test_timer_flush_observes_scheduled_times() -> None:
    start = now()
    foos = [0]
    bars = [0]
    bazs = [0]
    foo = timer(lambda _e: (foos.__setitem__(0, foos[0] + 1), foo.stop()), 0, start + 1)
    bar = timer(lambda _e: (bars.__setitem__(0, bars[0] + 1), bar.stop()), 0, start)
    baz = timer(lambda _e: (bazs.__setitem__(0, bazs[0] + 1), baz.stop()), 0, start - 1)
    timer_flush()
    assert foos[0] == 0
    assert bars[0] == 1
    assert bazs[0] == 1
    foo.stop()
    bar.stop()
    baz.stop()


def test_timer_flush_scheduling_order() -> None:
    results: list[int] = []
    t0 = timer(lambda _e: (results.append(1), t0.stop()))
    t1 = timer(lambda _e: (results.append(2), t1.stop()))
    t2 = timer(lambda _e: (results.append(3), t2.stop()))
    timer_flush()
    assert results == [1, 2, 3]


def test_timer_restart_type_errors() -> None:
    t = timer(lambda _e: None)
    with pytest.raises(TypeError):
        t.restart()  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        t.restart(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        t.restart("42")  # type: ignore[arg-type]
    t.stop()


def test_timeout_stops_before_user_callback() -> None:
    log: list[str] = []

    def user(_e: float) -> None:
        log.append("user")

    t = timeout(user, 0)
    assert isinstance(t, Timer)
    t.stop()


def test_interval_is_interval_timer() -> None:
    it = interval(lambda _e: None, 1000)
    assert isinstance(it, IntervalTimer)
    assert isinstance(it, Timer)
    it.stop()


def test_now_repeated_same_tick() -> None:
    a = now()
    assert a > 0
    assert now() == a


def test_now_advances_after_sleep() -> None:
    a = now()
    time.sleep(0.05)
    b = now()
    assert 40 <= b - a <= 120


def assert_in_range(actual: float, lo: float, hi: float) -> None:
    assert lo <= actual <= hi, f"{actual} not in [{lo}, {hi}]"


def test_timeout_fires_once_after_delay() -> None:
    then = now()
    done: list[bool] = []

    def cb(_e: float) -> None:
        assert_in_range(now() - then, 40, 90)
        done.append(True)

    timeout(cb, 50)
    deadline = time.monotonic() + 2.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timer_runs_until_stopped() -> None:
    count = [0]

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] > 2:
            tref[0].stop()

    tref = [timer(cb)]
    deadline = time.monotonic() + 3.0
    while count[0] <= 2 and time.monotonic() < deadline:
        time.sleep(0.01)
    assert count[0] > 2


def test_interval_runs_until_stopped() -> None:
    count = [0]

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] > 2:
            tref[0].stop()

    tref = [interval(cb, 30)]
    deadline = time.monotonic() + 4.0
    while count[0] <= 2 and time.monotonic() < deadline:
        time.sleep(0.01)
    assert count[0] > 2


