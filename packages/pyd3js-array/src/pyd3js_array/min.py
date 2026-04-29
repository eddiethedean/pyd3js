"""D3-compatible minimum reducer."""

from __future__ import annotations

from typing import Any, Callable, Optional

from pyd3js_array._compare import definite, gt


def min_(
    values: list[Any],
    valueof: Optional[Callable[[Any, int, list[Any]], Any]] = None,
) -> Any:
    """Return the minimum of *values*.

    Matches `d3.min` semantics:

    - Ignores `None` values.
    - Ignores non-definite values (e.g. `NaN`).
    - If *valueof* is provided, it is called as `valueof(d, i, values)` and its return value is
      used for comparisons.

    Returns:
        The minimum observed value, or `None` if no observed values are present.
    """
    out: Any = None
    if valueof is None:
        for value in values:
            if value is None:
                continue
            if not definite(value):
                continue
            if out is None:
                out = value
            elif gt(out, value):
                out = value
    else:
        index = -1
        for item in values:
            index += 1
            value = valueof(item, index, values)
            if value is None:
                continue
            if not definite(value):
                continue
            if out is None:
                out = value
            elif gt(out, value):
                out = value
    return out
