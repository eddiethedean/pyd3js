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
    nums = list(iter_observed_numbers(values, valueof))
    nums.sort()
    return quantileSorted(nums, p)
