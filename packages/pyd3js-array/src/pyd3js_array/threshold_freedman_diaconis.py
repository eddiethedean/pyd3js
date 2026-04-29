"""D3-compatible `thresholdFreedmanDiaconis`."""

from __future__ import annotations

import math

from pyd3js_array.count import count
from pyd3js_array.quantile import quantile


def thresholdFreedmanDiaconis(values: list[float], min: float, max: float) -> int:
    """Return a recommended bin count using the Freedman–Diaconis rule.

    Mirrors `d3.thresholdFreedmanDiaconis(values, min, max)`.
    """

    n = count(values)
    if n <= 0:
        return 1
    q75 = quantile(values, 0.75)
    q25 = quantile(values, 0.25)
    if q75 is None or q25 is None:  # pragma: no cover
        return 1
    iqr = q75 - q25
    if iqr == 0:
        return 1
    width = 2 * iqr * (n ** (-1 / 3))
    if width == 0:  # pragma: no cover
        return 1
    k = (max - min) / width
    if not math.isfinite(k) or k <= 0:
        return 1
    return int(math.ceil(k))


__all__ = ["thresholdFreedmanDiaconis"]

