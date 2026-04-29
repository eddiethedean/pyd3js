"""D3-compatible bisector factory.

This module mirrors the behavior of `d3.bisector`:

- If passed a one-argument callable, it is treated as an **accessor** and the
  bisector compares `accessor(d)` to `x`.
- Otherwise it is treated as a **comparator** and the bisector compares `d` to `x`
  using the supplied comparator.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast, overload

from pyd3js_array._typing import CompareFn, SupportsOrdering

T = TypeVar("T")
U = TypeVar("U")


def _is_accessor(fn: Callable[..., object]) -> bool:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return False
    params = [
        p
        for p in sig.parameters.values()
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    return len(params) == 1


def _ascending(a: object, b: object) -> int:
    """Internal ascending comparator used for accessor-based bisectors.

    This intentionally uses Python ordering (`<`/`>`) rather than D3's full mixed-type
    ordering rules; it matches upstream `d3.bisector(accessor)` behavior where the
    accessor projection is typically numeric or otherwise naturally ordered.
    """
    aa = cast(SupportsOrdering, a)
    bb = cast(SupportsOrdering, b)
    if aa < bb:
        return -1
    if aa > bb:
        return 1
    return 0


@dataclass(frozen=True)
class Bisector(Generic[T]):
    _compare: Callable[[object, object], float | int]
    _accessor: Callable[[T], object] | None = None

    def left(self, a: list[T], x: object, lo: int = 0, hi: int | None = None) -> int:
        if hi is None:
            hi = len(a)
        if self._accessor is None:
            compare = self._compare
            while lo < hi:
                mid = (lo + hi) >> 1
                if compare(a[mid], x) < 0:  # type: ignore[arg-type]
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        acc = self._accessor
        compare = _ascending
        while lo < hi:
            mid = (lo + hi) >> 1
            if compare(acc(a[mid]), x) < 0:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def right(self, a: list[T], x: object, lo: int = 0, hi: int | None = None) -> int:
        if hi is None:
            hi = len(a)
        if self._accessor is None:
            compare = self._compare
            while lo < hi:
                mid = (lo + hi) >> 1
                if compare(a[mid], x) <= 0:  # type: ignore[arg-type]
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        acc = self._accessor
        compare = _ascending
        while lo < hi:
            mid = (lo + hi) >> 1
            if compare(acc(a[mid]), x) <= 0:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def center(self, a: list[T], x: object, lo: int = 0, hi: int | None = None) -> int:
        if hi is None:
            hi = len(a)
        i = self.left(a, x, lo, hi)
        if i <= lo:
            return i
        if i >= hi:
            return i - 1
        left_val = a[i - 1]
        right_val = a[i]
        if self._accessor is not None:
            acc = self._accessor
            left_v = acc(left_val)
            right_v = acc(right_val)
        else:
            left_v = left_val
            right_v = right_val
        # D3's center bisect compares distance; this is only meaningful for numeric values.
        xx = cast(float, x)
        lv = cast(float, left_v)
        rv = cast(float, right_v)
        return i - 1 if xx - lv < rv - xx else i


@overload
def bisector(compare_or_accessor: Callable[[T], U]) -> Bisector[T]: ...


@overload
def bisector(compare_or_accessor: CompareFn[T]) -> Bisector[T]: ...


def bisector(compare_or_accessor: Callable[..., object]) -> Bisector[object]:
    """Create a bisector.

    Matches `d3.bisector`.

    Args:
        compare_or_accessor:
            Either an accessor `f(d) -> x` (one positional argument), or a comparator
            `cmp(a, b) -> number` (two positional arguments).

    Returns:
        A `Bisector` instance with `left`, `right`, and `center` methods.

    Notes:
        - `center` computes a distance comparison (`x - left < right - x`) and is
          therefore only meaningful when the compared values are numeric.
    """

    # Overload-style behavior at runtime:
    # - 1 positional arg: accessor (T -> U)
    # - otherwise: comparator (U, U) -> number
    if _is_accessor(compare_or_accessor):
        return cast(Bisector[object], Bisector(_ascending, compare_or_accessor))
    return Bisector(cast(Callable[[object, object], float | int], compare_or_accessor))
