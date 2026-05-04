"""interpolateString — port of d3-interpolate `string.js`."""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from typing import Any

from pyd3js_interpolate.number import interpolate_number

_RE_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?")


def _js_string_number(x: float) -> str:
    """Format interpolated numbers like JS default string concatenation."""
    if isinstance(x, float):
        if x != x:
            return "NaN"
        if math.isinf(x):
            return "Infinity" if x > 0 else "-Infinity"
    rx = round(x)
    if abs(x - rx) < 1e-12:
        return str(int(rx))
    s = format(x, ".16g")
    if "e" in s or "E" in s:
        return s
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def interpolate_string(a: Any, b: Any) -> Callable[[float], str]:
    a = str(a)
    b = str(b)
    s: list[str | None] = []
    q: list[tuple[int, Callable[[float], float]]] = []
    bi = 0
    i = -1

    a_it = _RE_NUM.finditer(a)
    while True:
        am_m = next(a_it, None)
        if am_m is None:
            break
        am = am_m.group(0)
        bm_m = _RE_NUM.search(b, bi)
        if bm_m is None:
            break
        bs_idx = bm_m.start()
        if bs_idx > bi:
            bs = b[bi:bs_idx]
            if i >= 0 and s[i] is not None:
                s[i] += bs
            else:
                i += 1
                s.append(bs)
        bm = bm_m.group(0)
        if am == bm:
            if i >= 0 and s[i] is not None:
                s[i] += bm
            else:
                i += 1
                s.append(bm)
        else:
            i += 1
            s.append(None)
            q.append((i, interpolate_number(float(am), float(bm))))
        bi = bm_m.end()

    if bi < len(b):
        bs = b[bi:]
        if i >= 0 and s[i] is not None:
            s[i] += bs
        else:
            i += 1
            s.append(bs)

    if len(s) < 2:
        if q:
            inner = q[0][1]

            def one(_t: float) -> str:
                return _js_string_number(inner(_t))

            return one
        return lambda _t: b

    def multi(t: float) -> str:
        out = [("" if x is None else x) for x in s]
        for idx, interp in q:
            out[idx] = _js_string_number(interp(t))
        return "".join(out)

    return multi


__all__ = ["interpolate_string"]
