"""Constant helper (mirrors d3-contour constant.js)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

__all__ = ["constant"]


def constant(x: T) -> Callable[..., T]:
    def f(*_args: Any, **_kwargs: Any) -> T:
        return x

    return f
