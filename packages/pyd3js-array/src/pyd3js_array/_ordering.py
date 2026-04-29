"""Ordering utilities for D3-compatible comparisons."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._compare import gt, lt


def default_compare(a: Any, b: Any) -> int:
    """Default comparator for `least`/`greatest` helpers.

    Returns:
        `-1` if `a < b`, `1` if `a > b`, else `0`.
    """
    if lt(a, b):
        return -1
    if gt(a, b):
        return 1
    return 0


CompareFn = Callable[[Any, Any], float | int]
