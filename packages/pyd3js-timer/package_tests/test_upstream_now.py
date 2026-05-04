"""Port of d3-timer ``test/now-test.js``."""

from __future__ import annotations

import time

from pyd3js_timer import now

from upstream_support import assert_in_range


def test_now_returns_same_time_when_called_repeatedly() -> None:
    then = now()
    assert then > 0
    assert now() == then


def test_now_returns_different_time_after_delay() -> None:
    then = now()
    assert then > 0
    time.sleep(0.05)
    assert_in_range(now() - then, 40.0, 70.0)
