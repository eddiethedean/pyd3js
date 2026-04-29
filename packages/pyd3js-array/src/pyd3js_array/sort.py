"""D3-compatible `sort`."""

from __future__ import annotations

import inspect
import math
from collections.abc import Callable, Iterable
from functools import cmp_to_key
from typing import TypeVar, cast, overload

from pyd3js_array.ascending import ascending
from pyd3js_array._typing import CompareFn, CompareResult, SupportsOrdering

T = TypeVar("T")
K = TypeVar("K")
OK = TypeVar("OK", bound=SupportsOrdering)


def _cmp_int(cmp: Callable[[T, T], CompareResult], a: T, b: T) -> int:
    r = cmp(a, b)
    if isinstance(r, float) and math.isnan(r):
        return 0
    if r < 0:
        return -1
    if r > 0:
        return 1
    return 0


def _positional_arity(fn: Callable[..., object]) -> int | None:
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


@overload
def sort(values: Iterable[T]) -> list[T]: ...


@overload
def sort(values: Iterable[T], compare_or_key: Callable[[T], OK]) -> list[T]: ...


@overload
def sort(values: Iterable[T], compare_or_key: CompareFn[T]) -> list[T]: ...


def sort(
    values: Iterable[T], compare_or_key: Callable[..., object] | None = None
) -> list[T]:
    """Return a sorted copy of *values*.

    Mirrors `d3.sort(values[, comparatorOrAccessor])`.

    Notes:
        - The input iterable is not mutated; this returns a new `list`.
        - If *compare_or_key* accepts one positional argument, it is treated as a
          key/accessor function (like JavaScript's accessor form).
        - Otherwise it is treated as a comparator, returning a numeric sign.
        - `NaN` comparator results are treated as equality (`0`), matching D3's
          "defined" ordering behavior in practice.
    """

    out = list(values)
    if compare_or_key is None:
        out.sort(key=cmp_to_key(lambda a, b: _cmp_int(ascending, a, b)))
        return out

    # Heuristic: one-arg callable acts like an accessor; otherwise comparator.
    argc = _positional_arity(compare_or_key)
    if argc == 1:
        key_fn = cast(Callable[[T], OK], compare_or_key)
        decorated = [(key_fn(v), i, v) for i, v in enumerate(out)]
        decorated.sort(key=lambda t: t[0])
        out = [v for _, __, v in decorated]
        return out

    cmp_fn = cast(CompareFn[T], compare_or_key)
    out.sort(key=cmp_to_key(lambda a, b: _cmp_int(cmp_fn, a, b)))
    return out
