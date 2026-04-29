"""D3-compatible bisector factory."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


def _is_accessor(fn: Callable[..., Any]) -> bool:
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


def _ascending(a: Any, b: Any) -> int:
    # Minimal internal comparator for bisecting. Public `ascending` is added in a later Phase 2 step.
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


@dataclass(frozen=True)
class Bisector(Generic[T]):
    _compare: Callable[[Any, Any], float | int]
    _accessor: Callable[[T], Any] | None = None

    def left(self, a: list[T], x: Any, lo: int = 0, hi: int | None = None) -> int:
        if hi is None:
            hi = len(a)
        if self._accessor is None:
            compare = self._compare
            while lo < hi:
                mid = (lo + hi) >> 1
                if compare(a[mid], x) < 0:
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

    def right(self, a: list[T], x: Any, lo: int = 0, hi: int | None = None) -> int:
        if hi is None:
            hi = len(a)
        if self._accessor is None:
            compare = self._compare
            while lo < hi:
                mid = (lo + hi) >> 1
                if compare(a[mid], x) <= 0:
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

    def center(self, a: list[T], x: Any, lo: int = 0, hi: int | None = None) -> int:
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
        return i - 1 if x - left_v < right_v - x else i


def bisector(compare_or_accessor: Callable[..., Any]) -> Bisector[Any]:
    """Create a bisector.

    Matches `d3.bisector`:\n
    - If given a one-argument function, treat it as an accessor.\n
    - Otherwise, treat it as a comparator.\n
    """

    if _is_accessor(compare_or_accessor):
        return Bisector(_ascending, compare_or_accessor)  # type: ignore[arg-type]
    return Bisector(compare_or_accessor)  # type: ignore[arg-type]

