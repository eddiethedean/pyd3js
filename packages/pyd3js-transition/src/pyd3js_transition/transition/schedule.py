from __future__ import annotations

import threading
from typing import Any, Callable

from pyd3js_dispatch import dispatch
from pyd3js_timer import timer as d3_timer
from pyd3js_timer import timeout as d3_timeout

# States (match upstream)
CREATED = 0
SCHEDULED = 1
STARTING = 2
STARTED = 3
RUNNING = 4
ENDING = 5
ENDED = 6

_empty_on = dispatch("start", "end", "cancel", "interrupt")
_empty_tween: list[Any] = []

_SCHED_LOCK = threading.RLock()
_DEFER_MS = 1.0


def _defer_start_retry(
    timeout_fn: Any,
    start_fn: Callable[[float], Any],
    elapsed: float,
    delay_ms: float,
) -> None:
    """Defer ``start_fn(elapsed)`` so we do not re-enter within the same flush (d3-transition)."""
    timeout_fn(lambda _e: start_fn(elapsed), delay_ms)


def _tick_skip_idle_state(state: int) -> bool:
    """Return True if ``_tick`` should no-op for this schedule ``state``."""
    return state not in (STARTED, RUNNING, ENDING)


def schedule(
    node: Any,
    name: str | None,
    id: int,
    index: int,
    group: list[Any],
    timing: dict[str, Any],
) -> None:
    with _SCHED_LOCK:
        schedules = getattr(node, "__transition__", None)
        if schedules is None:
            schedules = {}
            setattr(node, "__transition__", schedules)
        elif id in schedules:
            return

        schedules[id] = {
            "name": name,
            "index": index,
            "group": group,
            "on": _empty_on,
            "tween": _empty_tween,
            "time": timing["time"],
            "delay": float(timing["delay"]),
            "duration": float(timing["duration"]),
            "ease": timing["ease"],
            "timer": None,
            "state": CREATED,
        }
        _create(node, id, schedules[id])


def init(node: Any, id: int) -> dict[str, Any]:
    with _SCHED_LOCK:
        s = get(node, id)
        if s["state"] > CREATED:
            raise RuntimeError("too late; already scheduled")
        return s


def set_(node: Any, id: int) -> dict[str, Any]:
    with _SCHED_LOCK:
        s = get(node, id)
        if s["state"] > STARTED:
            raise RuntimeError("too late; already running")
        return s


# Upstream name (d3-transition uses `set`).
def set(node: Any, id: int) -> dict[str, Any]:  # noqa: A001
    return set_(node, id)


def get(node: Any, id: int) -> dict[str, Any]:
    schedules = getattr(node, "__transition__", None)
    if not schedules or id not in schedules:
        raise RuntimeError("transition not found")
    return schedules[id]


def _create(node: Any, id: int, self: dict[str, Any]) -> None:
    schedules = getattr(node, "__transition__")
    tween: list[Callable[[Any, float], Any]] = []

    def _schedule_cb(elapsed: float) -> None:
        with _SCHED_LOCK:
            self["state"] = SCHEDULED
            self["timer"].restart(_start, self["delay"], self["time"])
            if self["delay"] <= elapsed:
                _start(elapsed - self["delay"])

    def _start(elapsed: float) -> None:
        with _SCHED_LOCK:
            if self["state"] != SCHEDULED:
                return _stop()  # pragma: no cover

            # Resolve interrupts/cancels for same-name transitions.
            for key in list(schedules.keys()):
                other = schedules[key]
                if other["name"] != self["name"]:
                    continue
                if other["state"] == STARTED:  # pragma: no cover
                    _defer_start_retry(d3_timeout, _start, elapsed, _DEFER_MS)
                    return
                if other["state"] == RUNNING:
                    other["state"] = ENDED
                    other["timer"].stop()
                    other["on"].call(
                        "interrupt",
                        node,
                        getattr(node, "__data__", None),
                        other["index"],
                        other["group"],
                    )
                    schedules.pop(key, None)
                elif int(key) < id:
                    other["state"] = ENDED
                    other["timer"].stop()
                    other["on"].call(
                        "cancel",
                        node,
                        getattr(node, "__data__", None),
                        other["index"],
                        other["group"],
                    )
                    schedules.pop(key, None)

            self["state"] = STARTING
            try:
                self["on"].call(
                    "start",
                    node,
                    getattr(node, "__data__", None),
                    self["index"],
                    self["group"],
                )
            except Exception:
                _stop()
                raise
            if self["state"] != STARTING:
                return
            self["state"] = STARTED

            # Initialize tween list, dropping None.
            raw = self["tween"]
            tween.clear()
            try:
                for tw in raw:
                    v = tw["value"](
                        node,
                        getattr(node, "__data__", None),
                        self["index"],
                        self["group"],
                    )
                    if v is not None:
                        tween.append(v)
            except Exception:
                _stop()
                raise

            # If the transition was cancelled/ended during tween initialization
            # (e.g. via selection.interrupt inside a tween factory), do not
            # restart the timer or invoke ticks.
            if self["state"] != STARTED:
                return

            # Switch the transition timer from `start` to `tick` before the next wake,
            # preventing a second `start` invocation from stopping the transition.
            # Keep state as STARTED until the first tick runs (matches upstream).
            self["timer"].restart(_tick, self["delay"], self["time"])
        # Match upstream behavior: invoke the first tick in the same logical frame.
        _tick(elapsed)

    def _tick(elapsed: float) -> None:
        with _SCHED_LOCK:
            if _tick_skip_idle_state(self["state"]):
                return  # pragma: no cover
            if self["state"] == STARTED:
                self["state"] = RUNNING

        duration = self["duration"]
        if elapsed < duration:
            t = self["ease"](elapsed / duration)
        else:
            self["timer"].restart(_stop)
            self["state"] = ENDING
            t = 1.0

        for fn in tween:
            # Tweens are generated as `(this, t) -> None` callables.
            try:
                fn(node, t)
            except Exception:
                _stop()
                raise

        if self["state"] == ENDING:
            try:
                self["on"].call(
                    "end",
                    node,
                    getattr(node, "__data__", None),
                    self["index"],
                    self["group"],
                )
            except Exception:
                _stop()
                raise
            _stop()

    def _stop() -> None:
        with _SCHED_LOCK:
            self["state"] = ENDED
            self["timer"].stop()
            schedules.pop(id, None)
            if not schedules:
                try:
                    delattr(node, "__transition__")
                except Exception:
                    pass

    self["timer"] = d3_timer(_schedule_cb, 0, self["time"])

