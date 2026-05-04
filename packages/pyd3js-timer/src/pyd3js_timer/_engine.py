"""
d3-timer core: Timer, timer, now, timer_flush, and the internal scheduler.

Semantics follow https://github.com/d3/d3-timer (v3). Browser timers are mapped
to :class:`threading.Timer` (17ms “frame” steps and long-delay wakes).
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable

# --- wall clock (override in tests via _set_wall_ms_factory) ----------------

_t0 = time.perf_counter()
_wall_ms_factory: Callable[[], float] | None = None


def _default_wall_ms() -> float:
    return (time.perf_counter() - _t0) * 1000.0


def _wall_ms() -> float:
    return _wall_ms_factory() if _wall_ms_factory is not None else _default_wall_ms()


def _set_wall_ms_factory(factory: Callable[[], float] | None) -> None:
    """Test hook: replace wall ms source (monotonic). None restores default."""
    global _wall_ms_factory
    _wall_ms_factory = factory


# --- module state (d3-timer/timer.js) ---------------------------------------

_frame = 0
_timeout_flag = 0
_interval_flag = 0
_poke_delay_ms = 1000.0
_task_head: Timer | None = None
_task_tail: Timer | None = None
_clock_last = 0.0
_clock_now = 0.0
_clock_skew = 0.0

_lock = threading.RLock()

_frame_timer: threading.Timer | None = None
_wake_timer: threading.Timer | None = None
_poke_timer: threading.Timer | None = None
_clear_now_timer: threading.Timer | None = None

FRAME_MS = 17.0
LONG_DELAY_MS = 24.0


def _cancel_timer(t: threading.Timer | None) -> None:
    if t is not None:
        t.cancel()


def _set_frame(fn: Callable[[], None]) -> None:
    global _frame_timer
    _cancel_timer(_frame_timer)
    t = threading.Timer(FRAME_MS / 1000.0, fn)
    t.daemon = True
    t.start()
    _frame_timer = t


def _clear_now() -> None:
    global _clock_now
    with _lock:
        _clock_now = 0.0


def now() -> float:
    """Current time in milliseconds (monotonic skew layer, d3-timer ``now``)."""
    global _clock_now, _clear_now_timer
    with _lock:
        if _clock_now != 0.0:
            return _clock_now
        _cancel_timer(_clear_now_timer)
        t = threading.Timer(FRAME_MS / 1000.0, _clear_now)
        t.daemon = True
        t.start()
        _clear_now_timer = t
        _clock_now = _wall_ms() + _clock_skew
        return _clock_now


class Timer:
    __slots__ = ("_call", "_time", "_next")

    def __init__(self) -> None:
        self._call: Callable[[float], Any] | None = None
        self._time = 0.0
        self._next: Timer | None = None

    def restart(self, callback: Callable[[float], Any], delay: Any = None, time: Any = None) -> None:
        global _task_head, _task_tail
        if not callable(callback):
            raise TypeError("callback is not a function")
        with _lock:
            t_abs = (now() if time is None else float(time)) + (0.0 if delay is None else float(delay))
            if self._next is None and _task_tail is not self:
                if _task_tail is not None:
                    _task_tail._next = self
                else:
                    _task_head = self
                _task_tail = self
            self._call = callback
            self._time = t_abs
            _sleep()

    def stop(self) -> None:
        with _lock:
            if self._call is not None:
                self._call = None
                self._time = float("inf")
                _sleep()


def timer(
    callback: Callable[[float], Any],
    delay: Any = None,
    time: Any = None,
) -> Timer:
    t = Timer()
    t.restart(callback, delay, time)
    return t


def timer_flush() -> None:
    """Run every due timer callback synchronously (d3 ``timerFlush``)."""
    global _frame
    now()  # refresh clock
    with _lock:
        _frame += 1
        try:
            t = _task_head
            clock = _clock_now
            while t is not None:
                nxt = t._next
                if t._call is not None:
                    e = clock - t._time
                    if e >= 0:
                        t._call(e)
                t = nxt
        finally:
            _frame -= 1


def _wake() -> None:
    global _clock_now, _frame, _timeout_flag, _clock_last
    with _lock:
        _clock_last = _wall_ms()
        _clock_now = _clock_last + _clock_skew
        _frame = 0
        _timeout_flag = 0
    try:
        timer_flush()
    finally:
        with _lock:
            _frame = 0
            _nap()
            _clock_now = 0.0


def _poke() -> None:
    global _clock_skew, _clock_last
    with _lock:
        w = _wall_ms()
        delay = w - _clock_last
        if delay > _poke_delay_ms:
            _clock_skew -= delay
            _clock_last = w


def _schedule_next_poke_iteration(chain: Callable[[], None]) -> None:
    """Queue the next skew probe (``setInterval`` analogue)."""
    global _poke_timer
    with _lock:
        if _interval_flag:
            nxt = threading.Timer(_poke_delay_ms / 1000.0, chain)
            nxt.daemon = True
            nxt.start()
            _poke_timer = nxt


def _create_poke_chain() -> Callable[[], None]:
    def _poke_chain() -> None:
        _poke()
        _schedule_next_poke_iteration(_poke_chain)

    return _poke_chain


def _nap() -> None:
    global _task_head, _task_tail
    t0: Timer | None = None
    t1 = _task_head
    t_next_time = float("inf")
    while t1 is not None:
        if t1._call is not None:
            if t_next_time > t1._time:
                t_next_time = t1._time
            t0 = t1
            t1 = t1._next
        else:
            t2 = t1._next
            t1._next = None
            if t0 is not None:
                t0._next = t2
            else:
                _task_head = t2
            t1 = t2
    _task_tail = t0
    _sleep(t_next_time)


def _sleep(time: float | None = None) -> None:
    global _frame, _timeout_flag, _interval_flag, _wake_timer, _poke_timer, _clock_last
    with _lock:
        if _frame:
            return
        if _timeout_flag:
            _cancel_timer(_wake_timer)
            _wake_timer = None
            _timeout_flag = 0
        # ``sleep()`` from restart passes no time (JS: undefined - clockNow => NaN);
        # nap passes the next wake time.
        if time is None:
            delay = float("nan")
        else:
            delay = time - _clock_now
        if delay > LONG_DELAY_MS:
            if time is not None and time < float("inf"):
                ms = time - _wall_ms() - _clock_skew
                sec = max(0.0, ms / 1000.0)

                def _fire() -> None:
                    global _timeout_flag, _wake_timer
                    with _lock:
                        _timeout_flag = 0
                        _wake_timer = None
                    _wake()

                _wake_timer = threading.Timer(sec, _fire)
                _wake_timer.daemon = True
                _wake_timer.start()
                _timeout_flag = 1
            if _interval_flag:
                _cancel_timer(_poke_timer)
                _poke_timer = None
                _interval_flag = 0
        else:
            if not _interval_flag:
                _clock_last = _wall_ms()
                _interval_flag = 1

                first = threading.Timer(_poke_delay_ms / 1000.0, _create_poke_chain())
                first.daemon = True
                first.start()
                _poke_timer = first
            _frame = 1
            _set_frame(_wake)


def timeout(
    callback: Callable[[float], Any],
    delay: Any = None,
    time: Any = None,
) -> Timer:
    """Invoke *callback* once after *delay* ms (d3 ``timeout``)."""
    t = Timer()
    d = 0.0 if delay is None else float(delay)

    def wrapped(elapsed: float) -> None:
        t.stop()
        callback(elapsed + d)

    t.restart(wrapped, delay, time)
    return t


def interval(
    callback: Callable[[float], Any],
    delay: Any = None,
    time: Any = None,
) -> IntervalTimer:
    """Repeatedly invoke *callback* every *delay* ms (d3 ``interval``)."""
    it = IntervalTimer()
    it.restart(callback, delay, time)
    return it


class IntervalTimer(Timer):
    """Timer whose ``restart`` reschedules as a repeating interval when *delay* is set."""

    def restart(self, callback: Callable[[float], Any], delay: Any = None, time: Any = None) -> None:
        if delay is None:
            return super().restart(callback, delay, time)
        d = float(delay)
        t_anchor = now() if time is None else float(time)
        total = d

        def tick(elapsed: float) -> None:
            nonlocal total
            elapsed_user = elapsed + total
            total += d
            Timer.restart(self, tick, total, t_anchor)
            callback(elapsed_user)

        Timer.restart(self, tick, d, t_anchor)


# Back-compat alias for D3 naming
timerFlush = timer_flush

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


def _reset_for_tests() -> None:
    """Clear scheduler state and cancel pending timers (tests only)."""
    global _frame, _timeout_flag, _interval_flag, _poke_delay_ms
    global _task_head, _task_tail, _clock_last, _clock_now, _clock_skew
    global _frame_timer, _wake_timer, _poke_timer, _clear_now_timer
    with _lock:
        _poke_delay_ms = 1000.0
        _cancel_timer(_frame_timer)
        _frame_timer = None
        _cancel_timer(_wake_timer)
        _wake_timer = None
        _cancel_timer(_poke_timer)
        _poke_timer = None
        _cancel_timer(_clear_now_timer)
        _clear_now_timer = None
        _timeout_flag = 0
        _interval_flag = 0
        _frame = 0
        t = _task_head
        while t is not None:
            n = t._next
            t._call = None
            t._next = None
            t = n
        _task_head = None
        _task_tail = None
        _clock_last = 0.0
        _clock_now = 0.0
        _clock_skew = 0.0
