"""D3-compatible `quantileIndex`."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pyd3js_array._compare import tonumber
from pyd3js_array.max_index import maxIndex
from pyd3js_array.min_index import minIndex


def quantileIndex(
    values: list[Any],
    p: float,
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> int | None:
    """Return the index (in *values*) of the p-quantile.

    Mirrors `d3.quantileIndex(values, p[, valueof])`.

    Unlike `quantile`, this function preserves the *original indices*: it coerces each
    element to a number (with invalid values becoming `NaN`), then selects an index as
    if performing an order-statistic selection on those coerced numbers.
    """

    if isinstance(p, float) and math.isnan(p):
        return None
    p = float(p)

    if valueof is None:
        nums = [tonumber(v) for v in values]
    else:
        nums = [tonumber(valueof(v, i, values)) for i, v in enumerate(values)]

    if p <= 0:
        return minIndex(nums)
    if p >= 1:
        return maxIndex(nums)

    j = len(nums) - 1
    if j < 0:
        return None

    i = int(math.floor(j * p))

    def _invalid(x: float) -> bool:
        return not (x == x)

    # Sort indices by the upstream `ascendingDefined` ordering:
    # invalid values (null/NaN) sort after defined values.
    sorted_idx = sorted(
        range(len(nums)),
        key=lambda k: (_invalid(nums[k]), nums[k] if not _invalid(nums[k]) else 0.0),
    )

    # Choose the greatest numeric value among the smallest i+1 indices.
    best = -1
    best_value = float("-inf")
    for k in sorted_idx[: i + 1]:
        x = nums[k]
        if _invalid(x):
            continue
        if best == -1 or x > best_value:
            best = k
            best_value = x
    return best


__all__ = ["quantileIndex"]

