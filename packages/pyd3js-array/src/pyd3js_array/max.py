"""D3-compatible maximum reducer."""

from __future__ import annotations

from typing import TypeVar, overload

from pyd3js_array._compare import definite, lt
from pyd3js_array._typing import AccessorFn

T = TypeVar("T")
R = TypeVar("R")


@overload
def max_(values: list[T]) -> T | None: ...


@overload
def max_(values: list[T], valueof: AccessorFn[T, R]) -> R | None: ...


def max_(values: list[T], valueof: AccessorFn[T, R] | None = None) -> T | R | None:
    """Return the maximum of *values*.

    Matches `d3.max` semantics:

    - Ignores `None` values.
    - Ignores non-definite values (e.g. `NaN`).
    - If *valueof* is provided, it is called as `valueof(d, i, values)` and its return value is
      used for comparisons.

    Returns:
        The maximum observed value, or `None` if no observed values are present.
    """
    out: T | R | None = None
    if valueof is None:
        for value in values:
            if value is None:
                continue
            if not definite(value):
                continue
            if out is None:
                out = value
            elif lt(out, value):
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
            elif lt(out, value):
                out = value
    return out
