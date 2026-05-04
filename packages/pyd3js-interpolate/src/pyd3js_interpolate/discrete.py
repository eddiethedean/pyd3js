"""interpolateDiscrete — port of d3-interpolate `discrete.js`."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


def interpolate_discrete(range_vals: Sequence[T]) -> Callable[[float], T]:
    n = len(range_vals)

    def f(t: float) -> T:
        idx = int(max(0, min(n - 1, math.floor(t * n))))
        return range_vals[idx]

    return f


__all__ = ["interpolate_discrete"]
