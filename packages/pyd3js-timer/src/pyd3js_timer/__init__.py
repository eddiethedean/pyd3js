"""
pyd3js-timer — Python port of d3-timer.

Public API mirrors d3-timer (``now``, ``timer``, ``timerFlush`` / ``timer_flush``,
``timeout``, ``interval``).
"""

from __future__ import annotations

from pyd3js_timer._engine import (
    IntervalTimer,
    Timer,
    interval,
    now,
    timer,
    timer_flush,
    timerFlush,
    timeout,
)

__version__ = "0.1.0"

__all__ = [
    "IntervalTimer",
    "Timer",
    "interval",
    "now",
    "timer",
    "timer_flush",
    "timerFlush",
    "timeout",
]
