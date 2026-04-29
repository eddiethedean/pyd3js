"""D3-compatible `sort`."""

from __future__ import annotations

import inspect
import math
from collections.abc import Callable, Iterable
from functools import cmp_to_key
from typing import Any, TypeVar

from pyd3js_array.ascending import ascending

T = TypeVar("T")


def _cmp_int(cmp: Callable[[Any, Any], Any], a: Any, b: Any) -> int:
    r = cmp(a, b)
    if isinstance(r, float) and math.isnan(r):
        return 0
    if r < 0:
        return -1
    if r > 0:
        return 1
    return 0


def _positional_arity(fn: Callable[..., Any]) -> int | None:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return None
    params = [
        p
        for p in sig.parameters.values()
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    return len(params)


def sort(
    values: Iterable[T],
    compare_or_key: Callable[..., Any] | None = None,
) -> list[T]:
    """Return a sorted copy of *values*.

    Mirrors `d3.sort(values[, comparatorOrAccessor])`.
    """

    out = list(values)
    if compare_or_key is None:
        out.sort(key=cmp_to_key(lambda a, b: _cmp_int(ascending, a, b)))
        return out

    # Heuristic: one-arg callable acts like an accessor; otherwise comparator.
    argc = _positional_arity(compare_or_key)
    if argc == 1:
        key_fn = compare_or_key  # type: ignore[assignment]
        out.sort(key=lambda d: key_fn(d))  # type: ignore[misc]
        return out

    cmp_fn = compare_or_key  # type: ignore[assignment]
    out.sort(key=cmp_to_key(lambda a, b: _cmp_int(cmp_fn, a, b)))
    return out

