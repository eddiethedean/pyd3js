"""D3-compatible quantile helper."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers
from pyd3js_array.quantile_sorted import quantileSorted


def quantile(
    values: list[Any],
    p: float,
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    """Compute the p-quantile of *values*.

    Matches `d3.quantile` semantics:

    - Filters/coerces inputs to numbers and ignores values that coerce to `NaN`.
    - Sorts numerically ascending before computing the quantile.
    - Clamps `p <= 0` to the minimum and `p >= 1` to the maximum.
    - Uses linear interpolation between adjacent ranks.
    - Returns `None` when no observed values are present.

    Args:
        values: Input array.
        p: Quantile in `[0, 1]` (values outside are clamped).
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        The quantile value, or `None` if empty after filtering.
    """
    nums = list(iter_observed_numbers(values, valueof))
    nums.sort()
    return quantileSorted(nums, p)
