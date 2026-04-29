"""D3-compatible `thresholdScott`."""

from __future__ import annotations

import math

from pyd3js_array.count import count
from pyd3js_array.deviation import deviation


def thresholdScott(values: list[float], min: float, max: float) -> int:
    """Return a recommended bin count using Scott's normal reference rule.

    Mirrors `d3.thresholdScott(values, min, max)`.
    """

    n = count(values)
    if n <= 0:
        return 1
    s = deviation(values)
    if s is None or s == 0:
        return 1
    k = (max - min) * (n ** (1 / 3)) / (3.49 * s)
    if not math.isfinite(k) or k <= 0:
        return 1
    return int(math.ceil(k))


__all__ = ["thresholdScott"]

