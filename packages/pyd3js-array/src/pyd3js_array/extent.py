"""D3-compatible extent (min/max) reducer."""

from __future__ import annotations

from typing import Any, Callable, Optional, Tuple, Union

from pyd3js_array._compare import definite, gt, lt

Maybe = Union[Any, None]


def extent(
    values: list[Any],
    valueof: Optional[Callable[[Any, int, list[Any]], Any]] = None,
) -> Tuple[Maybe, Maybe]:
    """Return the minimum and maximum of *values* as a `(min, max)` tuple.

    Matches `d3.extent` semantics:

    - Ignores `None` values.
    - Ignores non-definite values (e.g. `NaN`, or objects whose `valueOf()` yields `NaN`).
    - Uses D3-like comparison rules for mixed types (see `_compare.gt/lt`).
    - If *valueof* is provided, it is called as `valueof(d, i, values)` and its return value is
      used for comparisons.

    Args:
        values: Input array.
        valueof: Optional accessor called with `(d, i, values)`.

    Returns:
        A tuple `(min, max)`. Returns `(None, None)` when no observed values are present.
    """
    min_v: Maybe = None
    max_v: Maybe = None
    if valueof is None:
        for value in values:
            if value is None:
                continue
            if not definite(value):
                continue
            if min_v is None:
                min_v = max_v = value
            else:
                if gt(min_v, value):
                    min_v = value
                if lt(max_v, value):
                    max_v = value
    else:
        idx = -1
        for item in values:
            idx += 1
            value = valueof(item, idx, values)
            if value is None:
                continue
            if not definite(value):
                continue
            if min_v is None:
                min_v = max_v = value
            else:
                if gt(min_v, value):
                    min_v = value
                if lt(max_v, value):
                    max_v = value
    return (min_v, max_v)
