from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t


def easeQuadIn(t: Any) -> float:
    t = ease_t(t)
    return t * t


def easeQuadOut(t: Any) -> float:
    t = ease_t(t)
    return t * (2.0 - t)


def easeQuadInOut(t: Any) -> float:
    t = ease_t(t)
    t *= 2.0
    if t <= 1.0:
        return t * t / 2.0
    t -= 1.0
    return (t * (2.0 - t) + 1.0) / 2.0


easeQuad = easeQuadInOut

__all__ = [
    "easeQuad",
    "easeQuadIn",
    "easeQuadInOut",
    "easeQuadOut",
]
