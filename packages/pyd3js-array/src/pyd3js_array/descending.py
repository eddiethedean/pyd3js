"""D3-compatible `descending` comparator."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array._compare import tonumber


def descending(a: Any, b: Any) -> float:
    """Compare *a* and *b* in descending order.

    Matches `d3.descending` semantics.
    """

    if isinstance(a, str) and isinstance(b, str):
        if a < b:
            return 1.0
        if a > b:
            return -1.0
        return 0.0

    na = tonumber(a)
    nb = tonumber(b)
    if math.isnan(na) or math.isnan(nb):
        return float("nan")
    if na < nb:
        return 1.0
    if na > nb:
        return -1.0
    return 0.0
