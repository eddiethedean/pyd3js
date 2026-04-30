# ruff: noqa: E741 — D3 uses `l` for Lab luminance / HCL lightness.
"""CIELAB / HCL color spaces — port of d3-color `lab.js`."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_color._math import degrees, radians
from pyd3js_color.color import Color, Rgb, _unary_plus, rgbConvert

K = 18.0
Xn = 0.96422
Yn = 1.0
Zn = 0.82521
t0 = 4.0 / 29.0
t1 = 6.0 / 29.0
t2 = 3.0 * t1 * t1
t3 = t1 * t1 * t1


def _xyz2lab(t: float) -> float:
    return math.pow(t, 1.0 / 3.0) if t > t3 else t / t2 + t0


def _lab2xyz(t: float) -> float:
    return t * t * t if t > t1 else t2 * (t - t0)


def _lrgb2rgb(x: float) -> float:
    return 255.0 * (
        (12.92 * x) if x <= 0.0031308 else (1.055 * math.pow(x, 1.0 / 2.4) - 0.055)
    )


def _rgb2lrgb(x: float) -> float:
    x = x / 255.0
    return x / 12.92 if x <= 0.04045 else math.pow((x + 0.055) / 1.055, 2.4)


class Lab(Color):
    __slots__ = ("l", "a", "b", "opacity")

    def __init__(self, l: Any, a: Any, b: Any, opacity: Any = 1.0) -> None:
        self.l = _unary_plus(l)
        self.a = _unary_plus(a)
        self.b = _unary_plus(b)
        self.opacity = 1.0 if opacity is None else _unary_plus(opacity)

    def brighter(self, k: float | None = None) -> Lab:
        kk = 1.0 if k is None else float(k)
        return Lab(self.l + K * kk, self.a, self.b, self.opacity)

    def darker(self, k: float | None = None) -> Lab:
        kk = 1.0 if k is None else float(k)
        return Lab(self.l - K * kk, self.a, self.b, self.opacity)

    def rgb(self) -> Rgb:
        y = (self.l + 16.0) / 116.0
        x = y if math.isnan(self.a) else y + self.a / 500.0
        z = y if math.isnan(self.b) else y - self.b / 200.0
        x = Xn * _lab2xyz(x)
        y = Yn * _lab2xyz(y)
        z = Zn * _lab2xyz(z)
        return Rgb(
            _lrgb2rgb(3.1338561 * x - 1.6168667 * y - 0.4906146 * z),
            _lrgb2rgb(-0.9787684 * x + 1.9161415 * y + 0.0334540 * z),
            _lrgb2rgb(0.0719453 * x - 0.2289914 * y + 1.4052427 * z),
            self.opacity,
        )


class Hcl(Color):
    __slots__ = ("h", "c", "l", "opacity")

    def __init__(self, h: Any, c: Any, l: Any, opacity: Any = 1.0) -> None:
        self.h = _unary_plus(h)
        self.c = _unary_plus(c)
        self.l = _unary_plus(l)
        self.opacity = 1.0 if opacity is None else _unary_plus(opacity)

    def brighter(self, k: float | None = None) -> Hcl:
        kk = 1.0 if k is None else float(k)
        return Hcl(self.h, self.c, self.l + K * kk, self.opacity)

    def darker(self, k: float | None = None) -> Hcl:
        kk = 1.0 if k is None else float(k)
        return Hcl(self.h, self.c, self.l - K * kk, self.opacity)

    def rgb(self) -> Rgb:
        return _hcl2lab(self).rgb()


def _hcl2lab(o: Hcl) -> Lab:
    if math.isnan(o.h):
        return Lab(o.l, 0.0, 0.0, o.opacity)
    hr = o.h * radians
    return Lab(o.l, math.cos(hr) * o.c, math.sin(hr) * o.c, o.opacity)


def labConvert(o: Any) -> Lab:
    if isinstance(o, Lab):
        return Lab(o.l, o.a, o.b, o.opacity)
    if isinstance(o, Hcl):
        return _hcl2lab(o)
    if not isinstance(o, Rgb):
        o = rgbConvert(o)
    r = _rgb2lrgb(o.r)
    g = _rgb2lrgb(o.g)
    b = _rgb2lrgb(o.b)
    y = _xyz2lab((0.2225045 * r + 0.7168786 * g + 0.0606169 * b) / Yn)
    if r == g == b:
        x = z = y
    else:
        x = _xyz2lab((0.4360747 * r + 0.3850649 * g + 0.1430804 * b) / Xn)
        z = _xyz2lab((0.0139322 * r + 0.0971045 * g + 0.7141733 * b) / Zn)
    return Lab(116.0 * y - 16.0, 500.0 * (x - y), 200.0 * (y - z), o.opacity)


def gray(l: Any, opacity: Any = None) -> Lab:
    op = 1.0 if opacity is None else _unary_plus(opacity)
    return Lab(l, 0.0, 0.0, op)


def lab(*args: Any) -> Lab:
    if len(args) == 1:
        return labConvert(args[0])
    if len(args) == 3:
        l, a, b = args
        return Lab(l, a, b, 1.0)
    if len(args) == 4:
        l, a, b, opacity = args
        return Lab(l, a, b, opacity)
    return Lab(float("nan"), float("nan"), float("nan"), float("nan"))


def hclConvert(o: Any) -> Hcl:
    if isinstance(o, Hcl):
        return Hcl(o.h, o.c, o.l, o.opacity)
    if not isinstance(o, Lab):
        o = labConvert(o)
    if o.a == 0 and o.b == 0:
        return Hcl(
            float("nan"),
            0.0 if 0 < o.l < 100 else float("nan"),
            o.l,
            o.opacity,
        )
    h = math.atan2(o.b, o.a) * degrees
    if h < 0:
        h += 360.0
    c = math.sqrt(o.a * o.a + o.b * o.b)
    return Hcl(h, c, o.l, o.opacity)


def hcl(*args: Any) -> Hcl:
    if len(args) == 1:
        return hclConvert(args[0])
    if len(args) == 3:
        h, c, l = args
        return Hcl(h, c, l, 1.0)
    if len(args) == 4:
        h, c, l, opacity = args
        return Hcl(h, c, l, 1.0 if opacity is None else opacity)
    return Hcl(float("nan"), float("nan"), float("nan"), float("nan"))


def lch(*args: Any) -> Hcl:
    if len(args) == 1:
        return hclConvert(args[0])
    if len(args) == 3:
        l, c, h = args
        return Hcl(h, c, l, 1.0)
    if len(args) == 4:
        l, c, h, opacity = args
        return Hcl(h, c, l, 1.0 if opacity is None else opacity)
    return Hcl(float("nan"), float("nan"), float("nan"), float("nan"))
