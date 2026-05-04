"""Decompose 2D affine matrix — port of d3-interpolate `transform/decompose.js`."""

from __future__ import annotations

import math

_degrees = 180.0 / math.pi

IDENTITY: dict[str, float] = {
    "translateX": 0.0,
    "translateY": 0.0,
    "rotate": 0.0,
    "skewX": 0.0,
    "scaleX": 1.0,
    "scaleY": 1.0,
}


def decompose(
    a: float, b: float, c: float, d: float, e: float, f: float
) -> dict[str, float]:
    scale_x: float
    scale_y: float
    skew_x: float
    if scale_x := math.sqrt(a * a + b * b):
        a /= scale_x
        b /= scale_x
    if skew_x := a * c + b * d:
        c -= a * skew_x
        d -= b * skew_x
    if scale_y := math.sqrt(c * c + d * d):
        c /= scale_y
        d /= scale_y
        skew_x /= scale_y
    if a * d < b * c:
        a = -a
        b = -b
        skew_x = -skew_x
        scale_x = -scale_x
    return {
        "translateX": e,
        "translateY": f,
        "rotate": math.atan2(b, a) * _degrees,
        "skewX": math.atan(skew_x) * _degrees,
        "scaleX": scale_x,
        "scaleY": scale_y,
    }


__all__ = ["IDENTITY", "decompose"]
