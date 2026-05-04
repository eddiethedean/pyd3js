"""interpolateNumberArray — port of d3-interpolate `numberArray.js`."""

from __future__ import annotations

from array import array
from collections.abc import Callable
from typing import Any


def is_number_array(x: Any) -> bool:
    return isinstance(x, array) and x.typecode in "bBhHiIlLqQfd"


def _to_float(x: Any, i: int) -> float:
    return float(x[i])


def _store(tc: str, c: array, i: int, v: float) -> None:
    if tc in "fd":
        c[i] = v
        return
    if tc == "B":
        c[i] = int(v) & 0xFF
        return
    if tc == "b":
        iv = int(round(v)) & 0xFF
        if iv >= 0x80:
            iv -= 0x100
        c[i] = iv
        return
    if tc == "I":
        c[i] = int(v) & 0xFFFFFFFF
        return
    if tc == "L":
        c[i] = int(v) & 0xFFFFFFFFFFFFFFFF
        return
    if tc in "hi":
        iv = int(round(v)) & 0xFFFF
        if iv >= 0x8000:
            iv -= 0x10000
        c[i] = iv
        return
    if tc in "Hl":
        if tc == "H":
            c[i] = int(v) & 0xFFFF
        else:
            c[i] = int(v) & 0xFFFFFFFF
        return
    if tc == "q":
        iv = int(round(v)) & 0xFFFFFFFFFFFFFFFF
        if iv >= 2**63:
            iv -= 2**64
        c[i] = iv
        return
    if tc == "Q":
        c[i] = int(v) & 0xFFFFFFFFFFFFFFFF
        return
    c[i] = int(round(v))  # pragma: no cover


def interpolate_number_array(a: Any, b: Any) -> Callable[[float], array]:
    if not b:
        b = array("d")
    nb = len(b)
    na = min(nb, len(a)) if a else 0
    if not isinstance(b, array):
        msg = "interpolate_number_array expects array.array as b"
        raise TypeError(msg)
    tc = b.typecode
    c = array(tc, b)

    def f(t: float) -> array:
        for i in range(na):
            v = _to_float(a, i) * (1.0 - t) + _to_float(b, i) * t
            _store(tc, c, i, v)
        return c

    return f


__all__ = ["interpolate_number_array", "is_number_array"]
