from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers


def variance(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    # Sample variance using a Welford-style stable update.
    n = 0
    mean = 0.0
    m2 = 0.0
    for x in iter_observed_numbers(values, valueof):
        n += 1
        delta = x - mean
        mean += delta / n
        m2 += delta * (x - mean)

    if n < 2:
        return None
    return m2 / (n - 1)
