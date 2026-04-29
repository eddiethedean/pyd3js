"""JavaScript-style relational comparisons for D3 array operations."""

from __future__ import annotations

import math
from typing import Any, Callable, SupportsFloat, SupportsIndex, Union


def _is_nan(x: Any) -> bool:
    try:
        return isinstance(x, float) and math.isnan(x)
    except TypeError:
        return False


def tonumber(x: Any) -> float:
    if x is None:
        return float("nan")
    if isinstance(x, bool):
        return 1.0 if x else 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        if s == "":
            return float("nan")
        try:
            return float(s)
        except ValueError:
            return float("nan")
    value_of = getattr(x, "valueOf", None)
    if callable(value_of):
        return tonumber(value_of())
    return float("nan")


NumberLike = Union[SupportsFloat, SupportsIndex, str, Any]


def definite(x: Any) -> bool:
    """True if x is usable as an observed value (mirrors `x >= x` for primitives)."""
    if x is None:
        return False
    if _is_nan(x):
        return False
    value_of = getattr(x, "valueOf", None)
    if callable(value_of):
        try:
            v = value_of()
        except Exception:
            return False
        return definite(v)
    try:
        return x == x  # noqa: PLR0124
    except Exception:
        return False


def gt(a: NumberLike, b: NumberLike) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return a > b
    na, nb = tonumber(a), tonumber(b)
    if _is_nan(na) or _is_nan(nb):
        return False
    return na > nb


def lt(a: NumberLike, b: NumberLike) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return a < b
    na, nb = tonumber(a), tonumber(b)
    if _is_nan(na) or _is_nan(nb):
        return False
    return na < nb


Accessor = Callable[[Any, int, list[Any]], Any]
