"""D3-compatible `nice` helper."""

from __future__ import annotations

import math

from pyd3js_array.tick_increment import tickIncrement


def nice(start: float, stop: float, count: float) -> tuple[float, float]:
    """Expand a domain to 'nice' round numbers.

    Matches `d3.nice` semantics:

    - If `stop < start`, returns the original `(start, stop)` (no-op).
    - Uses `tickIncrement(start, stop, count)` to compute the step.
    """

    start = float(start)
    stop = float(stop)
    count = float(count)

    if math.isnan(start) or math.isnan(stop) or math.isnan(count):
        return (start, stop)
    if stop < start:
        return (start, stop)
    if count <= 0 or start == stop:
        return (start, stop)

    inc = tickIncrement(start, stop, count)
    if inc is None or inc != inc or inc == 0:
        return (start, stop)

    step = inc if inc > 0 else -1.0 / inc
    return (math.floor(start / step) * step, math.ceil(stop / step) * step)

