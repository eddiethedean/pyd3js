"""interpolateHue — port of d3-interpolate `hue.js`."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pyd3js_interpolate._color_interpolate import hue as hue_channel


def interpolate_hue(a: Any, b: Any) -> Callable[[float], float]:
    i = hue_channel(float(a), float(b))

    def f(t: float) -> float:
        x = i(t)
        if isinstance(x, float) and math.isnan(x):
            return x
        return x - 360.0 * math.floor(x / 360.0)

    return f


__all__ = ["interpolate_hue"]
