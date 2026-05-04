"""interpolateBasisClosed — port of d3-interpolate `basisClosed.js`."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from pyd3js_interpolate.basis import basis_fn


def interpolate_basis_closed(values: Sequence[float]) -> Callable[[float], float]:
    n = len(values)

    def f(t: float) -> float:
        # Match JS `t = (t % 1 + 1) % 1` for negative inputs (Python `%` differs).
        t = t - math.floor(t)
        i = int(math.floor(t * n))
        v0 = values[(i + n - 1) % n]
        v1 = values[i % n]
        v2 = values[(i + 1) % n]
        v3 = values[(i + 2) % n]
        return basis_fn((t - i / n) * n, v0, v1, v2, v3)

    return f


__all__ = ["interpolate_basis_closed"]
