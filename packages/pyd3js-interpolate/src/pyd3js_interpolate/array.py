"""interpolateArray — port of d3-interpolate `array.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_interpolate.number_array import interpolate_number_array, is_number_array


def generic_array(a: Any, b: Any) -> Callable[[float], list[Any]]:
    from pyd3js_interpolate.value import interpolate_value

    nb = len(b) if b else 0
    na = min(nb, len(a)) if a is not None and hasattr(a, "__len__") else 0
    x = [interpolate_value(a[i], b[i]) for i in range(na)]
    c = [b[i] for i in range(nb)]

    def f(t: float) -> list[Any]:
        for i in range(na):
            c[i] = x[i](t)
        return c

    return f


def interpolate_array(a: Any, b: Any) -> Callable[[float], Any]:
    if is_number_array(b):
        return interpolate_number_array(a, b)
    return generic_array(a, b)


__all__ = ["generic_array", "interpolate_array"]
