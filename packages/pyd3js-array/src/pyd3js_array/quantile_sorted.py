"""D3-compatible quantile for pre-sorted numeric data."""

from __future__ import annotations

import math
from typing import TypeVar

from pyd3js_array._iter import iter_observed_numbers
from pyd3js_array._typing import AccessorFn

T = TypeVar("T")


def quantileSorted(
    values: list[T],
    p: float,
    valueof: AccessorFn[T, object] | None = None,
) -> float | None:
    """Compute the p-quantile of already-sorted values.

    Matches `d3.quantileSorted` semantics.

    The input is expected to be sorted numerically ascending. This function still applies the
    same observed-value filtering and numeric coercion as other reducers.

    Args:
        values: Sorted input array.
        p: Quantile in `[0, 1]` (values outside are clamped).
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        The quantile value, or `None` if empty after filtering.
    """
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
