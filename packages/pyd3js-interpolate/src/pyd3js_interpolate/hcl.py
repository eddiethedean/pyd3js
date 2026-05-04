"""interpolateHcl — port of d3-interpolate `hcl.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_color.lab import Hcl, hclConvert

from pyd3js_interpolate._color_interpolate import hue as hue_channel
from pyd3js_interpolate._color_interpolate import nogamma as color_channel


def _hcl_interp_convert(x: Any) -> Hcl:
    if x is None:
        return Hcl(float("nan"), float("nan"), float("nan"), float("nan"))
    return hclConvert(x)


def _hcl_factory(hue_interp: Callable[[float, float], Callable[[float], float]]):
    def hcl_interp(start: Any, end: Any) -> Callable[[float], str]:
        s = _hcl_interp_convert(start)
        e = _hcl_interp_convert(end)
        h = hue_interp(s.h, e.h)
        c = color_channel(s.c, e.c)
        l_ = color_channel(s.l, e.l)
        opacity = color_channel(s.opacity, e.opacity)

        def f(t: float) -> str:
            s.h = h(t)
            s.c = c(t)
            s.l = l_(t)
            s.opacity = opacity(t)
            return str(s)

        return f

    return hcl_interp


interpolate_hcl = _hcl_factory(hue_channel)
interpolate_hcl_long = _hcl_factory(color_channel)

__all__ = ["interpolate_hcl", "interpolate_hcl_long"]
