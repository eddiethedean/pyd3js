"""D3-compatible `tickIncrement` helper."""

from __future__ import annotations

import math


_E10 = math.sqrt(50)
_E5 = math.sqrt(10)
_E2 = math.sqrt(2)


def tickIncrement(start: float, stop: float, count: float) -> float | None:
    """Return the tick increment for a start/stop/count.

    Matches `d3.tickIncrement` semantics:

    - Returns `None` for non-positive `count` or non-finite inputs.
    - Returns `NaN` when `stop < start` (reversed domain).
    - Returns an integer step when the increment is >= 1, otherwise a negative reciprocal:
      e.g. step 0.2 -> `-5`.
    """

    start = float(start)
    stop = float(stop)
    count = float(count)

    if count <= 0 or math.isnan(start) or math.isnan(stop) or math.isnan(count):
        return None
    if not math.isfinite(start) or not math.isfinite(stop) or not math.isfinite(count):
        return None
    if stop < start:
        return float("nan")
    if stop == start:
        return 0.0

    step = (stop - start) / count
    power = math.floor(math.log10(step))
    error = step / (10**power)
    if error >= _E10:
        factor = 10
    elif error >= _E5:
        factor = 5
    elif error >= _E2:
        factor = 2
    else:
        factor = 1

    if power >= 0:
        return float(factor * (10**power))
    return float(-(10 ** (-power)) / factor)
