"""D3-compatible `cumsum`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from pyd3js_array._compare import tonumber


def cumsum(
    values: Iterable[Any],
    valueof: Callable[[Any, int, Iterable[Any]], Any] | None = None,
) -> list[float]:
    """Return the cumulative sum of *values*.

    Mirrors `d3.cumsum(values[, valueof])`:
    - Coerces each element to a number and treats invalid values as 0.
    - Returns a sequence the same length as the input.
    """

    out: list[float] = []
    total = 0.0
    if valueof is None:
        for v in values:
            x = tonumber(v)
            if x != x:
                x = 0.0
            total += x
            out.append(total)
    else:
        index = 0
        for v in values:
            x = tonumber(valueof(v, index, values))
            if x != x:
                x = 0.0
            total += x
            out.append(total)
            index += 1
    return out


__all__ = ["cumsum"]
