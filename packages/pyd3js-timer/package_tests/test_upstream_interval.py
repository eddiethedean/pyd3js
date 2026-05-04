"""Port of d3-timer ``test/interval-test.js``."""

from __future__ import annotations

import time

import pytest

from pyd3js_timer import Timer, interval, now

from upstream_support import assert_in_range


def test_interval_invokes_about_every_17ms() -> None:
    then = now()
    count = [0]
    done: list[bool] = []

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] > 10:
            t_holder[0].stop()
            assert_in_range(now() - then, (17.0 - 5.0) * count[0], (17.0 + 5.0) * count[0])
            done.append(True)

    t_holder: list = [interval(cb)]
    deadline = time.monotonic() + 5.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_interval_invokes_until_stopped() -> None:
    count = [0]
    done: list[bool] = []

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] > 2:
            t_holder[0].stop()
            done.append(True)

    t_holder: list = [interval(cb)]
    deadline = time.monotonic() + 4.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_interval_custom_delay_mean_rate() -> None:
    then = now()
    delay = 50.0
    nows: list[float] = [then]
    done: list[bool] = []

    def cb(_e: float) -> None:
        nows.append(now())
        if len(nows) > 10:
            t_holder[0].stop()
            for i, n in enumerate(nows):
                assert_in_range(n - then, delay * i - 25.0, delay * i + 25.0)
            done.append(True)

    t_holder: list = [interval(cb, delay)]
    deadline = time.monotonic() + 8.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_interval_delay_time_relative_to_given_time() -> None:
    then = now() + 50.0
    delay = 50.0
    done: list[bool] = []

    def cb(_e: float) -> None:
        assert_in_range(now() - then, delay - 15.0, delay + 15.0)
        t_holder[0].stop()
        done.append(True)

    t_holder: list = [interval(cb, delay, then)]
    deadline = time.monotonic() + 4.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


@pytest.mark.skip(reason="Python has no JS `this` binding for plain callbacks.")
def test_interval_uses_undefined_context() -> None:
    interval(lambda _e: None)


def test_interval_passes_elapsed_time() -> None:
    then = now()
    done: list[bool] = []

    def cb(elapsed: float) -> None:
        assert elapsed == now() - then
        t_holder[0].stop()
        done.append(True)

    t_holder: list = [interval(cb, 100)]
    deadline = time.monotonic() + 4.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_interval_returns_a_timer() -> None:
    count = [0]
    t = interval(lambda _e: count.__setitem__(0, count[0] + 1))
    assert isinstance(t, Timer)
    t.stop()
    time.sleep(0.12)
    assert count[0] == 0


def test_interval_restart_restarts_as_interval() -> None:
    then = now()
    delay = 50.0
    nows: list[float] = [then]
    done: list[bool] = []

    def callback(_e: float) -> None:
        nows.append(now())
        if len(nows) > 10:
            t_holder[0].stop()
            for i, n in enumerate(nows):
                assert_in_range(n - then, delay * i - 25.0, delay * i + 25.0)
            done.append(True)

    t_holder: list = [interval(callback, delay)]
    t_holder[0].stop()
    t_holder[0].restart(callback, delay)
    deadline = time.monotonic() + 8.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done
