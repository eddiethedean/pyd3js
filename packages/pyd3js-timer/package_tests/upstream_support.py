"""Helpers mirroring d3-timer Mocha tests (``asserts.js``, timing waits)."""

from __future__ import annotations

import time


def assert_in_range(actual: float, expected_min: float, expected_max: float) -> None:
    assert expected_min <= actual <= expected_max, (
        f"{actual} should be in range of [{expected_min}, {expected_max}]"
    )


def idle_ms(ms: float) -> None:
    time.sleep(ms / 1000.0)


def wait_until(deadline_monotonic: float, step: float = 0.01) -> None:
    while time.monotonic() < deadline_monotonic:
        time.sleep(step)
