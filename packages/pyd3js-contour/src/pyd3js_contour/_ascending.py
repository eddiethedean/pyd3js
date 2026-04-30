"""Numeric comparator (mirrors d3-contour ascending.js)."""

from __future__ import annotations

__all__ = ["ascending"]


def ascending(a: float, b: float) -> float:
    return a - b
