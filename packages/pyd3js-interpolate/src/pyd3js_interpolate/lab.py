"""interpolateLab — port of d3-interpolate `lab.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_color.lab import Lab, labConvert

from pyd3js_interpolate._color_interpolate import nogamma as color_channel


def _lab_interp_convert(x: Any) -> Lab:
    if x is None:
        return Lab(float("nan"), float("nan"), float("nan"), float("nan"))
    return labConvert(x)


def interpolate_lab(start: Any, end: Any) -> Callable[[float], str]:
    s = _lab_interp_convert(start)
    e = _lab_interp_convert(end)
    l_ = color_channel(s.l, e.l)
    a = color_channel(s.a, e.a)
    b_ = color_channel(s.b, e.b)
    opacity = color_channel(s.opacity, e.opacity)

    def f(t: float) -> str:
        s.l = l_(t)
        s.a = a(t)
        s.b = b_(t)
        s.opacity = opacity(t)
        return str(s)

    return f


__all__ = ["interpolate_lab"]
