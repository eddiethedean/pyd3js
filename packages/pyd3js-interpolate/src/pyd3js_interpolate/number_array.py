"""interpolateNumberArray — port of d3-interpolate `numberArray.js`."""

from __future__ import annotations

import re
from array import array
from collections.abc import Callable
from typing import Any


def _typecode_from_memoryview(mv: memoryview) -> str:
    if mv.ndim != 1:
        msg = "interpolateNumberArray expects a 1-D buffer"
        raise TypeError(msg)
    fmt = mv.format
    if not fmt:  # pragma: no cover — CPython memoryviews expose a format string
        msg = "memoryview must have a known format"
        raise TypeError(msg)
    base = re.sub(r"^[@=<>!]", "", fmt)
    if len(base) == 1 and base in "bBhHiIlLqQfd":
        return base
    if base in (
        "n",
        "N",
    ):  # pragma: no cover — not all array typecodes exist on every platform
        return "q" if mv.itemsize == 8 else "i"
    msg = f"unsupported memoryview format {fmt!r}"
    raise TypeError(msg)


def is_number_array(x: Any) -> bool:
    if isinstance(x, array):
        return x.typecode in "bBhHiIlLqQfd"
    if isinstance(x, memoryview):
        try:
            _typecode_from_memoryview(x)
        except TypeError:
            return False
        return True
    return False


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


def _backing_array_from_memoryview(mv: memoryview) -> array:
    tc = _typecode_from_memoryview(mv)
    c = array(tc)
    c.frombytes(mv.tobytes())
    return c


def interpolate_number_array(a: Any, b: Any) -> Callable[[float], array | memoryview]:
    """Interpolate numeric buffers; `b` may be array, memoryview, list, tuple, or None (like JS `!b`)."""
    return_mv = False
    if isinstance(b, memoryview):
        if len(b) == 0:
            b_arr = array("d")
        else:
            b_arr = _backing_array_from_memoryview(b)
            return_mv = True
    elif isinstance(b, array):
        b_arr = array(b.typecode, b)
    elif isinstance(b, (list, tuple)):
        b_arr = array("d", [float(x) for x in b]) if b else array("d")
    elif b is None:
        b_arr = array("d")
    else:
        msg = "interpolate_number_array expects b as array.array, memoryview, list, tuple, or None"
        raise TypeError(msg)

    nb = len(b_arr)

    if a is None:
        na = 0
    elif isinstance(a, (list, tuple, array, memoryview)):
        na = min(nb, len(a))
    else:
        msg = "interpolate_number_array expects a as None, list, tuple, array.array, or memoryview"
        raise TypeError(msg)

    tc = b_arr.typecode
    c = array(tc, b_arr)

    def f(t: float) -> array | memoryview:
        for i in range(na):
            v = _to_float(a, i) * (1.0 - t) + _to_float(b_arr, i) * t
            _store(tc, c, i, v)
        if return_mv:
            return memoryview(c)
        return c

    return f


__all__ = ["interpolate_number_array", "is_number_array"]
