"""interpolateHsl — port of d3-interpolate `hsl.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_color.color import Hsl, hslConvert

from pyd3js_interpolate._color_interpolate import hue as hue_channel
from pyd3js_interpolate._color_interpolate import nogamma as color_channel


def _hsl_interp_convert(x: Any) -> Hsl:
    if x is None:
        return Hsl(float("nan"), float("nan"), float("nan"), float("nan"))
    return hslConvert(x)


def _hsl_factory(hue_interp: Callable[[float, float], Callable[[float], float]]):
    def hsl_interp(start: Any, end: Any) -> Callable[[float], str]:
        s = _hsl_interp_convert(start)
        e = _hsl_interp_convert(end)
        h = hue_interp(s.h, e.h)
        sat = color_channel(s.s, e.s)
        light = color_channel(s.l, e.l)
        opacity = color_channel(s.opacity, e.opacity)

        def f(t: float) -> str:
            s.h = h(t)
            s.s = sat(t)
            s.l = light(t)
            s.opacity = opacity(t)
            return str(s)

        return f

    return hsl_interp


interpolate_hsl = _hsl_factory(hue_channel)
interpolate_hsl_long = _hsl_factory(color_channel)

__all__ = ["interpolate_hsl", "interpolate_hsl_long"]
