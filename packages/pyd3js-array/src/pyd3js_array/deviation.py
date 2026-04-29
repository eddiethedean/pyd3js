"""D3-compatible sample standard deviation reducer."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pyd3js_array.variance import variance


def deviation(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    """Return the sample standard deviation of the observed numeric values in *values*.

    Matches `d3.deviation` semantics:

    - Equivalent to `sqrt(variance(values))`.
    - Returns `None` when fewer than two observed values are present.

    Args:
        values: Input array.
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        Sample standard deviation, or `None` if insufficient observations.
    """
    v = variance(values, valueof)
    if v is None:
        return None
    return math.sqrt(v)
