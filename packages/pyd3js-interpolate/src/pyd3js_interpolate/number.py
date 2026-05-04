"""interpolateNumber — port of d3-interpolate `number.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def interpolate_number(a: Any, b: Any) -> Callable[[float], float]:
    a0, b0 = float(a), float(b)

    def f(t: float) -> float:
        return a0 * (1.0 - t) + b0 * t

    return f


__all__ = ["interpolate_number"]
