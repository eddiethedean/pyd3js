"""D3-compatible sample variance reducer."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers


def variance(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    """Return the sample variance of the observed numeric values in *values*.

    Matches `d3.variance` semantics:

    - Ignores `None` values.
    - Coerces inputs to numbers and ignores values that coerce to `NaN`.
    - Returns `None` when fewer than two observed values are present.

    The implementation uses a numerically stable Welford-style update.

    Args:
        values: Input array.
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        Sample variance, or `None` if insufficient observations.
    """
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
