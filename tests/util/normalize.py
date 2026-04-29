"""Normalize values for cross-language (Python / oracle JSON) comparison."""

from __future__ import annotations

import math
from typing import Any


def is_nan(x: Any) -> bool:
    try:
        return isinstance(x, float) and math.isnan(x)
    except TypeError:
        return False


def deep_equal(a: Any, b: Any, *, rel: float = 1e-12, abs_tol: float = 1e-12) -> bool:
    if is_nan(a) and is_nan(b):
        return True
    if a is None and b is None:
        return True
    if type(a) is not type(b) and not (
        isinstance(a, (int, float)) and isinstance(b, (int, float))
    ):
        return a == b
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=rel, abs_tol=abs_tol)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(deep_equal(x, y, rel=rel, abs_tol=abs_tol) for x, y in zip(a, b))
    return a == b


def assert_deep_equal(
    a: Any, b: Any, *, rel: float = 1e-12, abs_tol: float = 1e-12
) -> None:
    assert deep_equal(a, b, rel=rel, abs_tol=abs_tol), (a, b)


def sort_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: sort_keys(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [sort_keys(x) for x in obj]
    return obj
