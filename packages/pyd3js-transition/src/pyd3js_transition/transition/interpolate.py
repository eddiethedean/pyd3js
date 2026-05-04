from __future__ import annotations

from typing import Any, Callable

from pyd3js_color import color as d3_color
from pyd3js_interpolate import interpolate_number, interpolate_rgb, interpolate_string


def interpolate(a: Any, b: Any) -> Callable[[float], Any]:
    """
    Port of d3-transition's `transition/interpolate.js`.

    Picks interpolation strategy based on the *target* value b.
    """
    if isinstance(b, (int, float)):
        # JS `+null` is 0, and attribute/style reads return null when missing.
        if a is None:
            a_num = 0.0
        else:
            try:
                a_num = float(a)
            except Exception:
                a_num = float("nan")
        return interpolate_number(a_num, float(b))

    c = d3_color(b)
    if c is not None:
        return interpolate_rgb(a, c)

    return interpolate_string("" if a is None else a, "" if b is None else b)

