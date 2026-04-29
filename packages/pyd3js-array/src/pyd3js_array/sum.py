"""D3-compatible sum reducer."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers


def sum_(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float:
    """Return the sum of the observed numeric values in *values*.

    Matches `d3.sum` semantics:

    - Ignores `None` values.
    - Coerces inputs to numbers (e.g. `"2"` -> `2.0`, `True` -> `1.0`).
    - Ignores values that coerce to `NaN`.
    - Returns `0` when no observed values are present.

    Args:
        values: Input array.
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        The numeric sum as a float.
    """
    out = 0.0
    for n in iter_observed_numbers(values, valueof):
        out += n
    return out
