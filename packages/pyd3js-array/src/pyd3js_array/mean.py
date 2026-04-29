"""D3-compatible mean reducer."""

from __future__ import annotations

from typing import TypeVar

from pyd3js_array._iter import iter_observed_numbers
from pyd3js_array._typing import AccessorFn

T = TypeVar("T")


def mean(
    values: list[T],
    valueof: AccessorFn[T, object] | None = None,
) -> float | None:
    """Return the arithmetic mean of the observed numeric values in *values*.

    Matches `d3.mean` semantics:

    - Ignores `None` values.
    - Coerces inputs to numbers and ignores values that coerce to `NaN`.
    - Returns `None` when no observed values are present.

    Args:
        values: Input array.
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        The mean as a float, or `None` if empty after filtering.
    """
    total = 0.0
    count = 0
    for n in iter_observed_numbers(values, valueof):
        total += n
        count += 1
    if count == 0:
        return None
    return total / count
