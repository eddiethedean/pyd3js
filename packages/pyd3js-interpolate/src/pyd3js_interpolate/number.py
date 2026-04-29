from __future__ import annotations

from typing import Callable


def interpolateNumber(a: object, b: object) -> Callable[[float], float]:
    a0, b0 = float(a), float(b)

    def interpolate(t: float) -> float:
        return a0 * (1 - t) + b0 * t

    return interpolate


__all__ = ["interpolateNumber"]
