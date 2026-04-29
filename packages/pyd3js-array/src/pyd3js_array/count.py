"""D3-compatible `count`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from pyd3js_array._compare import tonumber


def count(
    values: Iterable[Any],
    valueof: Callable[[Any, int, Iterable[Any]], Any] | None = None,
) -> int:
    """Count the number of observed numeric values.

    Mirrors `d3.count(values[, valueof])`:
    - Ignores `None`.
    - Coerces to numbers and ignores values that coerce to `NaN`.
    """

    n = 0
    if valueof is None:
        for value in values:
            if value is None:
                continue
            x = tonumber(value)
            if x == x:
                n += 1
    else:
        index = -1
        for item in values:
            index += 1
            value = valueof(item, index, values)
            if value is None:
                continue
            x = tonumber(value)
            if x == x:
                n += 1
    return n


__all__ = ["count"]
