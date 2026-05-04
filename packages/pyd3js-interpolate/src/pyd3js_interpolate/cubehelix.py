"""interpolateCubehelix — port of d3-interpolate `cubehelix.js`."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pyd3js_color.cubehelix import Cubehelix, cubehelixConvert

from pyd3js_interpolate._color_interpolate import hue as hue_channel
from pyd3js_interpolate._color_interpolate import nogamma as color_channel


def _cube_interp_convert(x: Any) -> Cubehelix:
    if x is None:
        return Cubehelix(float("nan"), float("nan"), float("nan"), float("nan"))
    return cubehelixConvert(x)


def _build_cubehelix(
    hue_like: Callable[[float, float], Callable[[float], float]],
) -> Callable[[Any, Any], Callable[[float], str]]:
    def cubehelix_gamma(y_in: float) -> Callable[[Any, Any], Callable[[float], str]]:
        y = float(y_in)

        def pair(start: Any, end: Any) -> Callable[[float], str]:
            s = _cube_interp_convert(start)
            e = _cube_interp_convert(end)
            h = hue_like(s.h, e.h)
            sat = color_channel(s.s, e.s)
            light = color_channel(s.l, e.l)
            opacity = color_channel(s.opacity, e.opacity)

            def f(t: float) -> str:
                s.h = h(t)
                s.s = sat(t)
                s.l = light(math.pow(t, y))
                s.opacity = opacity(t)
                return str(s)

            return f

        return pair

    root = cubehelix_gamma(1.0)
    root.gamma = cubehelix_gamma  # type: ignore[attr-defined]
    return root


interpolate_cubehelix = _build_cubehelix(hue_channel)
interpolate_cubehelix_long = _build_cubehelix(color_channel)

__all__ = ["interpolate_cubehelix", "interpolate_cubehelix_long"]
