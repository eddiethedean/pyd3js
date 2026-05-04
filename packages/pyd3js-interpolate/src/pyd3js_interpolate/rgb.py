"""interpolateRgb — port of d3-interpolate `rgb.js`."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from pyd3js_color.color import Rgb, rgb as color_rgb
from pyd3js_color.color import rgbConvert

from pyd3js_interpolate._color_interpolate import gamma as gamma_factory
from pyd3js_interpolate._color_interpolate import nogamma
from pyd3js_interpolate.basis import interpolate_basis
from pyd3js_interpolate.basis_closed import interpolate_basis_closed


def _rgb_interp_convert(x: Any) -> Rgb:
    if x is None:
        return Rgb(float("nan"), float("nan"), float("nan"), float("nan"))
    return rgbConvert(x)


def _rgb_gamma(y_in: float) -> Callable[[Any, Any], Callable[[float], str]]:
    color = gamma_factory(y_in)

    def rgb_interp(start: Any, end: Any) -> Callable[[float], str]:
        s = _rgb_interp_convert(start)
        e = _rgb_interp_convert(end)
        r = color(s.r, e.r)
        g = color(s.g, e.g)
        b = color(s.b, e.b)
        opacity = nogamma(s.opacity, e.opacity)

        def f(t: float) -> str:
            s.r = r(t)
            s.g = g(t)
            s.b = b(t)
            s.opacity = opacity(t)
            return str(s)

        return f

    return rgb_interp


interpolate_rgb = _rgb_gamma(1.0)
interpolate_rgb.gamma = _rgb_gamma  # type: ignore[attr-defined]


def _rgb_spline(
    spline: Callable[[Sequence[float]], Callable[[float], float]],
) -> Callable[[Sequence[Any]], Callable[[float], str]]:
    def spline_interp(colors: Sequence[Any]) -> Callable[[float], str]:
        n = len(colors)
        r = [0.0] * n
        g = [0.0] * n
        b = [0.0] * n
        color = None
        for i in range(n):
            c = color_rgb(colors[i])
            color = c
            r[i] = (
                0.0
                if (isinstance(c.r, float) and math.isnan(c.r))
                else float(c.r or 0.0)
            )
            g[i] = (
                0.0
                if (isinstance(c.g, float) and math.isnan(c.g))
                else float(c.g or 0.0)
            )
            b[i] = (
                0.0
                if (isinstance(c.b, float) and math.isnan(c.b))
                else float(c.b or 0.0)
            )
        rf = spline(r)
        gf = spline(g)
        bf = spline(b)
        assert color is not None
        color.opacity = 1.0

        def f(t: float) -> str:
            color.r = rf(t)
            color.g = gf(t)
            color.b = bf(t)
            return str(color)

        return f

    return spline_interp


interpolate_rgb_basis = _rgb_spline(interpolate_basis)
interpolate_rgb_basis_closed = _rgb_spline(interpolate_basis_closed)

__all__ = [
    "interpolate_rgb",
    "interpolate_rgb_basis",
    "interpolate_rgb_basis_closed",
]
