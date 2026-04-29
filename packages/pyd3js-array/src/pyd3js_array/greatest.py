"""D3-compatible `greatest` helper."""

from __future__ import annotations

from typing import TypeVar

from pyd3js_array._iter import iter_observed
from pyd3js_array._ordering import default_compare
from pyd3js_array._typing import CompareFn

T = TypeVar("T")


def greatest(values: list[T], compare: CompareFn[T] | None = None) -> T | None:
    """Return the greatest element in *values* according to *compare*.

    Matches `d3.greatest` semantics:

    - Ignores `None` and non-definite values (`NaN`-like).
    - If *compare* is not provided, uses the default D3-like ordering (`_ordering.default_compare`).
    - If no observed values are present, returns `None`.

    Args:
        values: Input array.
        compare: Optional comparator `compare(a, b) -> number` where positive means `a > b`.

    Returns:
        The greatest observed value, or `None` if empty after filtering.
    """
    if compare is None:
        compare = default_compare

    it = iter_observed(values)
    best = next(it, None)
    if best is None:
        return None
    for v in it:
        if compare(v, best) > 0:
            best = v
    return best
