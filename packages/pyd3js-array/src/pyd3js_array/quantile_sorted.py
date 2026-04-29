from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers


def quantileSorted(
    values: list[Any],
    p: float,
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    nums = list(iter_observed_numbers(values, valueof))
    n = len(nums)
    if n == 0:
        return None
    if p <= 0:
        return nums[0]
    if p >= 1:
        return nums[-1]

    i = (n - 1) * p
    i0 = int(math.floor(i))
    v0 = nums[i0]
    v1 = nums[i0 + 1] if i0 + 1 < n else v0
    return v0 + (v1 - v0) * (i - i0)
