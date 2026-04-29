"""D3-compatible `tickStep` helper."""

from __future__ import annotations

from pyd3js_array.tick_increment import tickIncrement


def tickStep(start: float, stop: float, count: float) -> float | None:
    """Return the tick step size for a start/stop/count.

    Matches `d3.tickStep` semantics:

    - Returns `None` for non-positive `count` or non-finite inputs.
    - Returns a negative step when `start > stop`.
    """

    if count <= 0:
        return None
    if start == stop:
        return 0.0
    if stop < start:
        out = tickStep(stop, start, count)
        return None if out is None else -out

    inc = tickIncrement(start, stop, count)
    if inc is None:
        return None
    return inc if inc > 0 else -1.0 / inc
