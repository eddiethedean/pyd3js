from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t


def easeCubicIn(t: Any) -> float:
    t = ease_t(t)
    return t * t * t


def easeCubicOut(t: Any) -> float:
    t = ease_t(t)
    t -= 1.0
    return t * t * t + 1.0


def easeCubicInOut(t: Any) -> float:
    t = ease_t(t)
    t *= 2.0
    if t <= 1.0:
        return t * t * t / 2.0
    t -= 2.0
    return (t * t * t + 2.0) / 2.0


easeCubic = easeCubicInOut

__all__ = [
    "easeCubic",
    "easeCubicIn",
    "easeCubicInOut",
    "easeCubicOut",
]
