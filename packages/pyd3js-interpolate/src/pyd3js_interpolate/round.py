"""interpolateRound — port of d3-interpolate `round.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def interpolate_round(a: Any, b: Any) -> Callable[[float], int]:
    a0, b0 = float(a), float(b)

    def f(t: float) -> int:
        return int(round(a0 * (1.0 - t) + b0 * t))

    return f


__all__ = ["interpolate_round"]
