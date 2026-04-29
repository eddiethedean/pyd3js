"""D3-compatible `mode`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._compare import definite


def mode(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> Any | None:
    """Return the most-frequent observed value.

    Mirrors `d3.mode(values[, valueof])`:
    - Ignores `None` and non-definite values (`NaN`-like).
    - If there are multiple modes, returns the first encountered.
    """

    counts: dict[Any, int] = {}
    if valueof is None:
        for value in values:
            if value is None or not definite(value):
                continue
            counts[value] = counts.get(value, 0) + 1
    else:
        for i, item in enumerate(values):
            value = valueof(item, i, values)
            if value is None or not definite(value):
                continue
            counts[value] = counts.get(value, 0) + 1

    mode_value: Any | None = None
    mode_count = 0
    for value, c in counts.items():
        if c > mode_count:
            mode_count = c
            mode_value = value
    return mode_value


__all__ = ["mode"]
