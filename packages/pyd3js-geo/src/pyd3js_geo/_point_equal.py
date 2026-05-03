"""d3-geo `pointEqual.js`."""

from __future__ import annotations

from typing import Any, Sequence

epsilon = 1e-6


def point_equal(a: Sequence[Any], b: Sequence[Any]) -> bool:
    if a[0] is None or a[1] is None or b[0] is None or b[1] is None:
        return False
    return abs(a[0] - b[0]) < epsilon and abs(a[1] - b[1]) < epsilon
