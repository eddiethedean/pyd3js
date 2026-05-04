# pyd3js-timer user guide

## Purpose

`d3-timer` provides a small, efficient task queue for animation and delayed work: a monotonic `now()`, repeating `timer` callbacks, one-shot `timeout`, repeating `interval`, and synchronous `timer_flush()` for draining eligible callbacks.

## Imports

```python
from pyd3js_timer import (
    IntervalTimer,
    Timer,
    interval,
    now,
    timer,
    timer_flush,
    timerFlush,
    timeout,
)
```

Python idioms: prefer `timer_flush`; `timerFlush` exists for D3 naming parity.

## Callbacks

Every scheduled callback receives one argument: **elapsed** time in milliseconds (per d3-timer), not `this` (JavaScript). There is no `this` binding in Python.

## Threading

The port uses `threading.Timer` instead of the browser’s `requestAnimationFrame` / `setTimeout`. Callbacks may run on a background thread from a scheduled wake. For thread-safe use with shared mutable state, protect data with locks or marshal work back to a single thread (e.g. a UI main loop) as you would for any async timer.

## Synchronous drain

`timer_flush()` runs all due timers using the current logical clock, matching d3’s `timerFlush`. It is re-entrant and safe to call from inside a timer callback.

## When to use

- Animation-style loops (with `timer` or `interval`) when you want d3-style timing without a browser.
- One-shot delayed work (`timeout`) with the same delay API as d3.
- Tests that need deterministic control can use the internal test hooks in `pyd3js_timer._engine` (see `package_tests/`).
