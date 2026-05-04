"""Color channel interpolation helpers (d3-interpolate `color.js`)."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any


def constant(x: Any) -> Callable[[float], Any]:
    def f(_t: float) -> Any:
        return x

    return f


def linear(a: float, d: float) -> Callable[[float], float]:
    def f(t: float) -> float:
        return a + t * d

    return f


def exponential(a: float, b: float, y: float) -> Callable[[float], float]:
    a = math.pow(a, y)
    b = math.pow(b, y) - a
    inv_y = 1.0 / y

    def f(t: float) -> float:
        return math.pow(a + t * b, inv_y)

    return f


def _js_is_nan(x: float) -> bool:
    return math.isnan(x)


def _js_truthy_diff(d: float) -> bool:
    """JS `if (d)` is false for 0 and NaN; Python `if d` differs for NaN."""
    if _js_is_nan(d):
        return False
    return d != 0


def hue(a: float, b: float) -> Callable[[float], float]:
    d = b - a
    if _js_truthy_diff(d):
        if d > 180 or d < -180:
            d -= 360.0 * round(d / 360.0)
        return linear(a, d)
    return constant(b if _js_is_nan(a) else a)


def gamma(y_in: Any) -> Callable[[float, float], Callable[[float], float]]:
    y = float(y_in)
    if y == 1:
        return nogamma

    def gamma_interp(a: float, b: float) -> Callable[[float], float]:
        if _js_truthy_diff(b - a):
            return exponential(a, b, y)
        return constant(b if _js_is_nan(a) else a)

    return gamma_interp


def nogamma(a: float, b: float) -> Callable[[float], float]:
    d = b - a
    if _js_truthy_diff(d):
        return linear(a, d)
    return constant(b if _js_is_nan(a) else a)
