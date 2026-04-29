"""D3-compatible bisect helpers."""

from __future__ import annotations

from typing import Any

from pyd3js_array.bisector import bisector


_default = bisector(lambda a, b: -1 if a < b else (1 if a > b else 0))


def bisectLeft(a: list[Any], x: Any, lo: int = 0, hi: int | None = None) -> int:
    """Return the left insertion point for *x* in sorted list *a*."""

    return _default.left(a, x, lo, hi)


def bisectRight(a: list[Any], x: Any, lo: int = 0, hi: int | None = None) -> int:
    """Return the right insertion point for *x* in sorted list *a*."""

    return _default.right(a, x, lo, hi)


def bisectCenter(a: list[Any], x: Any, lo: int = 0, hi: int | None = None) -> int:
    """Return the index of the closest value to *x* in sorted list *a*."""

    return _default.center(a, x, lo, hi)

