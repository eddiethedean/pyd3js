"""quantize — port of d3-interpolate `quantize.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def quantize(interpolator: Callable[[float], Any], n: int) -> list[Any]:
    if n <= 0:
        return []
    return [interpolator(float("nan") if n == 1 else i / (n - 1)) for i in range(n)]


__all__ = ["quantize"]
