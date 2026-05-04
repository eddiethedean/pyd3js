"""Port of d3-timer ``test/timeout-test.js``."""

from __future__ import annotations

import time

import pytest

from pyd3js_timer import Timer, now, timeout

from upstream_support import assert_in_range


@pytest.mark.skip(reason="Python has no JS `this` binding for plain callbacks.")
def test_timeout_uses_undefined_context_for_callback() -> None:
    timeout(lambda _e: None)


def test_timeout_invokes_callback_once() -> None:
    count = [0]

    def cb(_e: float) -> None:
        count[0] += 1
        assert count[0] == 1

    timeout(cb)
    deadline = time.monotonic() + 2.0
    while count[0] < 1 and time.monotonic() < deadline:
        time.sleep(0.01)
    assert count[0] == 1


def test_timeout_delay_invokes_once_after_delay() -> None:
    then = now()
    done: list[bool] = []

    def cb(_e: float) -> None:
        assert_in_range(now() - then, 40.0, 70.0)
        done.append(True)

    timeout(cb, 50)
    deadline = time.monotonic() + 3.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timeout_delay_time_relative_to_given_time() -> None:
    then = now() + 50.0
    delay = 50.0
    done: list[bool] = []

    def cb(_e: float) -> None:
        assert_in_range(now() - then, delay - 15.0, delay + 15.0)
        done.append(True)

    timeout(cb, delay, then)
    deadline = time.monotonic() + 3.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timeout_passes_elapsed_time() -> None:
    then = now()
    done: list[bool] = []

    def cb(elapsed: float) -> None:
        assert elapsed == now() - then
        done.append(True)

    timeout(cb)
    deadline = time.monotonic() + 2.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)
    assert done


def test_timeout_returns_a_timer() -> None:
    count = [0]
    t = timeout(lambda _e: count.__setitem__(0, count[0] + 1))
    assert isinstance(t, Timer)
    t.stop()
    time.sleep(0.12)
    assert count[0] == 0
