"""D3-compatible `thresholdSturges`."""

from __future__ import annotations

import math
from collections.abc import Sequence

from pyd3js_array.count import count


def thresholdSturges(values: Sequence[float]) -> int:
    """Return a recommended bin count using Sturges' formula.

    Mirrors `d3.thresholdSturges(values)`.
    """

    n = count(values)
    if n <= 0:
        return 1
    return int(math.ceil(math.log(n, 2))) + 1


__all__ = ["thresholdSturges"]
