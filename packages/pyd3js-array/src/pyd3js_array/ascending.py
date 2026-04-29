"""D3-compatible `ascending` comparator."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array._compare import tonumber


def ascending(a: Any, b: Any) -> float:
    """Compare *a* and *b* in ascending order.

    Matches `d3.ascending` semantics:
    - returns -1, 0, 1 for ordered values
    - returns NaN if values are not comparable
    - if either coerces to NaN, returns NaN

    Note: JS `<` / `>` comparisons coerce mixed types; we approximate this by:
    - comparing strings lexicographically if both are strings
    - otherwise, attempting numeric coercion via `tonumber`
    """

    if isinstance(a, str) and isinstance(b, str):
        if a < b:
            return -1.0
        if a > b:
            return 1.0
        return 0.0

    na = tonumber(a)
    nb = tonumber(b)
    if math.isnan(na) or math.isnan(nb):
        return float("nan")
    if na < nb:
        return -1.0
    if na > nb:
        return 1.0
    return 0.0
