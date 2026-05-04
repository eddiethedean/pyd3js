"""interpolateBasis — port of d3-interpolate `basis.js`."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence


def basis_fn(t1: float, v0: float, v1: float, v2: float, v3: float) -> float:
    t2 = t1 * t1
    t3 = t2 * t1
    return (
        (1 - 3 * t1 + 3 * t2 - t3) * v0
        + (4 - 6 * t2 + 3 * t3) * v1
        + (1 + 3 * t1 + 3 * t2 - 3 * t3) * v2
        + t3 * v3
    ) / 6.0


def interpolate_basis(values: Sequence[float]) -> Callable[[float], float]:
    n = len(values) - 1

    def f(t: float) -> float:
        if t <= 0:
            t = 0.0
            seg = 0
        elif t >= 1:
            t = 1.0
            seg = max(0, n - 1)
        else:
            seg = int(math.floor(t * n))
        v1 = values[seg]
        v2 = values[seg + 1]
        v0 = values[seg - 1] if seg > 0 else 2 * v1 - v2
        v3 = values[seg + 2] if seg < n - 1 else 2 * v2 - v1
        return basis_fn((t - seg / n) * n, v0, v1, v2, v3)

    return f


__all__ = ["basis_fn", "interpolate_basis"]
