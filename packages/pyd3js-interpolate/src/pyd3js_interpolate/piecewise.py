"""piecewise — port of d3-interpolate `piecewise.js`."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any, overload


@overload
def piecewise(values: Sequence[Any]) -> Callable[[float], Any]: ...


@overload
def piecewise(
    interpolate: Callable[[Any, Any], Callable[[float], Any]],
    values: Sequence[Any],
) -> Callable[[float], Any]: ...


def piecewise(
    arg0: Any,
    arg1: Any | None = None,
) -> Callable[[float], Any]:
    from pyd3js_interpolate.value import interpolate_value

    if arg1 is None:
        interpolate_fn: Callable[[Any, Any], Callable[[float], Any]] = interpolate_value
        values: Sequence[Any] = arg0
    else:
        interpolate_fn = arg0
        values = arg1
    n = len(values) - 1
    i_list: list[Callable[[float], Any]] = []
    v = values[0]
    for j in range(n):
        v_next = values[j + 1]
        i_list.append(interpolate_fn(v, v_next))
        v = v_next

    def f(t: float) -> Any:
        tt = t * n
        seg = max(0, min(n - 1, int(math.floor(tt))))
        return i_list[seg](tt - seg)

    return f


__all__ = ["piecewise"]
