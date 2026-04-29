"""Shared iteration helpers for reducers.

These functions centralize D3-like filtering rules so reducers behave consistently:

- ignore `None`
- ignore non-definite values (e.g. `NaN`, or objects whose `valueOf()` yields/raises to `NaN`)
- for numeric reducers, coerce to numbers and ignore values that coerce to `NaN`
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Iterator
from typing import Any, TypeVar

from pyd3js_array._compare import definite, tonumber

T = TypeVar("T")


def iter_observed(
    values: list[T],
    valueof: Callable[[T, int, list[T]], Any] | None = None,
) -> Iterator[Any]:
    """Yield observed values, applying D3-style filtering and optional accessor.

    - Calls `valueof(d, i, values)` if provided.
    - Skips `None`.
    - Skips non-definite values (`NaN`, objects with `valueOf()` that returns/raises to NaN).
    """

    if valueof is None:
        for value in values:
            if value is None:
                continue
            if not definite(value):
                continue
            yield value
        return

    idx = -1
    for item in values:
        idx += 1
        value = valueof(item, idx, values)
        if value is None:
            continue
        if not definite(value):
            continue
        yield value


def iter_observed_numbers(
    values: list[T],
    valueof: Callable[[T, int, list[T]], Any] | None = None,
) -> Iterator[float]:
    """Yield observed values coerced to numbers.

    Values that coerce to `NaN` are skipped.
    """

    # Fast-path primitives to avoid `definite()` overhead on large numeric arrays.
    if valueof is None:
        for v in values:
            if v is None:
                continue
            if isinstance(v, float):
                if math.isnan(v):
                    continue
                yield v
                continue
            if isinstance(v, (int, bool, str)):
                n = tonumber(v)
                if n != n:  # NaN
                    continue
                yield n
                continue
            if not definite(v):
                continue
            n = tonumber(v)
            if n != n:  # NaN
                continue
            yield n
        return

    idx = -1
    for item in values:
        idx += 1
        v = valueof(item, idx, values)
        if v is None:
            continue
        if isinstance(v, float):
            if math.isnan(v):
                continue
            yield v
            continue
        if isinstance(v, (int, bool, str)):
            n = tonumber(v)
            if n != n:  # NaN
                continue
            yield n
            continue
        if not definite(v):
            continue
        n = tonumber(v)
        if n != n:  # NaN
            continue
        yield n


def first_observed(values: Iterable[Any]) -> Any | None:
    """Return the first element of an iterable, or `None` if empty."""
    for v in values:
        return v
    return None
