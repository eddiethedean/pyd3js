"""D3-compatible `medianIndex`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array.quantile_index import quantileIndex


def medianIndex(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> int | None:
    """Return the median index of *values*.

    Mirrors `d3.medianIndex(values[, valueof])`.
    """

    return quantileIndex(values, 0.5, valueof)


__all__ = ["medianIndex"]

