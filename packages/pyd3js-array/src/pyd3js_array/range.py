"""D3-compatible numeric range generator."""

from __future__ import annotations

import math
from typing import List


def range_(*args: float) -> List[float]:
    """Generate an arithmetic progression (like `d3.range`).

    This follows `d3.range` semantics:

    - `range(stop)` yields `[0, 1, ..., ceil(stop)-1]` for finite positive stops.
    - `range(start, stop[, step])` yields values starting at `start`, incrementing by `step`,
      stopping before `stop`.
    - Returns an empty list for invalid inputs such as `step == 0`, `NaN`, or infinite step
      sizes / counts.

    Args:
        *args: `(stop)`, `(start, stop)`, or `(start, stop, step)`.

    Returns:
        A list of floats.
    """
    if len(args) == 0:
        start, stop, step = 0.0, float("nan"), 1.0
    elif len(args) == 1:
        start, stop, step = 0.0, float(args[0]), 1.0
    elif len(args) == 2:
        start, stop, step = float(args[0]), float(args[1]), 1.0
    else:
        start, stop, step = float(args[0]), float(args[1]), float(args[2])
    if step == 0 or any(math.isnan(x) for x in (start, stop, step)):
        return []
    q = (stop - start) / step
    if math.isnan(q) or math.isinf(q):
        return []
    n = max(0, int(math.ceil(q)))
    return [start + i * step for i in range(n)]
