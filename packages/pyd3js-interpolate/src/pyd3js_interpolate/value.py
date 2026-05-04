"""interpolate — port of d3-interpolate `value.js`."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

from pyd3js_color.color import Color
from pyd3js_color.color import color as parse_color

from pyd3js_interpolate._color_interpolate import constant
from pyd3js_interpolate.array import generic_array
from pyd3js_interpolate.date import interpolate_date
from pyd3js_interpolate.number import coerce_unary_plus, interpolate_number
from pyd3js_interpolate.number_array import interpolate_number_array, is_number_array
from pyd3js_interpolate.object import interpolate_object
from pyd3js_interpolate.rgb import interpolate_rgb
from pyd3js_interpolate.string import interpolate_string


def _js_object_interpolator_path(b: Any) -> bool:
    """`value.js`: object branch when `ToNumber(b)` is NaN and `b` is not a primitive number."""
    n = coerce_unary_plus(b)
    return math.isnan(n) and not isinstance(b, float)


def interpolate_value(a: Any, b: Any) -> Callable[[float], Any]:
    if b is None or isinstance(b, bool):
        return constant(b)
    if isinstance(b, (int, float)) and not isinstance(b, bool):
        return interpolate_number(a, b)
    if isinstance(b, str):
        c = parse_color(b)
        if c is not None:
            return interpolate_rgb(a, c)
        return interpolate_string(a, b)
    if isinstance(b, Color):
        return interpolate_rgb(a, b)
    if isinstance(b, datetime):
        return interpolate_date(a, b)
    if is_number_array(b):
        return interpolate_number_array(a, b)
    if isinstance(b, (list, tuple)):
        return generic_array(a, b)
    if isinstance(b, Mapping) and not isinstance(b, (str, bytes)):
        return interpolate_object(a, b)

    if _js_object_interpolator_path(b):
        return interpolate_object(a, b)
    return interpolate_number(a, b)


__all__ = ["interpolate_value"]
