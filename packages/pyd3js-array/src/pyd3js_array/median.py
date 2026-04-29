"""D3-compatible median reducer."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array.quantile import quantile


def median(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    """Return the median of *values*.

    Matches `d3.median` semantics and is equivalent to `quantile(values, 0.5, valueof)`.

    Args:
        values: Input array.
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        Median value, or `None` if empty after filtering.
    """
    return quantile(values, 0.5, valueof)
