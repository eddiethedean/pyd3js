"""D3-compatible `minIndex`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._compare import definite, gt


def minIndex(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> int:
    """Return the index of the minimum observed value.

    Mirrors `d3.minIndex(values[, valueof])`:
    - Ignores `None` and non-definite values (`NaN`-like).
    - Returns -1 if no observed values are present.
    """

    best: Any = None
    best_i = -1
    if valueof is None:
        for i, value in enumerate(values):
            if value is None or not definite(value):
                continue
            if best is None or gt(best, value):
                best = value
                best_i = i
    else:
        for i, item in enumerate(values):
            value = valueof(item, i, values)
            if value is None or not definite(value):
                continue
            if best is None or gt(best, value):
                best = value
                best_i = i
    return best_i


__all__ = ["minIndex"]

