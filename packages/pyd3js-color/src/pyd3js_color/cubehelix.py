# ruff: noqa: E741 — D3 uses `l` for Cubehelix lightness.
"""Cubehelix color space — port of d3-color `cubehelix.js`."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_color._math import degrees, radians
from pyd3js_color.color import BRIGHTER, Color, DARKER, Rgb, _unary_plus, rgbConvert


A = -0.14861
B = +1.78277
C = -0.29227
D = -0.90649
E = +1.97294
ED = E * D
EB = E * B
BC_DA = B * C - D * A


class Cubehelix(Color):
    __slots__ = ("h", "s", "l", "opacity")

    def __init__(self, h: Any, s: Any, l: Any, opacity: Any = 1.0) -> None:
        self.h = _unary_plus(h)
        self.s = _unary_plus(s)
        self.l = _unary_plus(l)
        self.opacity = 1.0 if opacity is None else _unary_plus(opacity)

    def brighter(self, k: float | None = None) -> Cubehelix:
        kk = BRIGHTER if k is None else BRIGHTER ** float(k)
        return Cubehelix(self.h, self.s, self.l * kk, self.opacity)

    def darker(self, k: float | None = None) -> Cubehelix:
        kk = DARKER if k is None else DARKER ** float(k)
        return Cubehelix(self.h, self.s, self.l * kk, self.opacity)

    def rgb(self) -> Rgb:
        h = 0.0 if math.isnan(self.h) else (self.h + 120.0) * radians
        l = float(self.l)
        a = 0.0 if math.isnan(self.s) else self.s * l * (1.0 - l)
        cosh = math.cos(h)
        sinh = math.sin(h)
        return Rgb(
            255.0 * (l + a * (A * cosh + B * sinh)),
            255.0 * (l + a * (C * cosh + D * sinh)),
            255.0 * (l + a * (E * cosh)),
            self.opacity,
        )


def cubehelixConvert(o: Any) -> Cubehelix:
    if isinstance(o, Cubehelix):
        return Cubehelix(o.h, o.s, o.l, o.opacity)
    if not isinstance(o, Rgb):
        o = rgbConvert(o)
    r = o.r / 255.0
    g = o.g / 255.0
    b = o.b / 255.0
    l = (BC_DA * b + ED * r - EB * g) / (BC_DA + ED - EB)
    bl = b - l
    k = (E * (g - l) - C * bl) / D
    den = E * l * (1.0 - l)
    if den == 0:
        s = float("nan")
    else:
        s = math.sqrt(k * k + bl * bl) / den
    if not math.isnan(s) and s != 0:
        h = math.atan2(k, bl) * degrees - 120.0
    else:
        h = float("nan")
    if not math.isnan(h) and h < 0:
        h += 360.0
    return Cubehelix(h, s, l, o.opacity)


def cubehelix(*args: Any) -> Cubehelix:
    if len(args) == 1:
        return cubehelixConvert(args[0])
    if len(args) == 3:
        h, s, l = args
        return Cubehelix(h, s, l, 1.0)
    if len(args) == 4:
        h, s, l, opacity = args
        return Cubehelix(h, s, l, 1.0 if opacity is None else opacity)
    return Cubehelix(float("nan"), float("nan"), float("nan"), float("nan"))
