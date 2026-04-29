"""D3-compatible `Adder`, `fsum`, and `fcumsum`."""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from typing import Any

from pyd3js_array._compare import tonumber


class Adder:
    """Full-precision floating point adder (ported from upstream d3-array)."""

    __slots__ = ("_partials", "_n")

    def __init__(self) -> None:
        self._partials = [0.0] * 32
        self._n = 0

    def add(self, x: float) -> "Adder":
        p = self._partials
        i = 0
        for j in range(min(self._n, 32)):
            y = p[j]
            hi = x + y
            lo = x - (hi - y) if abs(x) < abs(y) else y - (hi - x)
            if lo:
                p[i] = lo
                i += 1
            x = hi
        p[i] = x
        self._n = i + 1
        return self

    def valueOf(self) -> float:
        p = self._partials
        n = self._n
        hi = 0.0
        lo = 0.0
        if n > 0:
            n -= 1
            hi = p[n]
            while n > 0:
                x = hi
                n -= 1
                y = p[n]
                hi = x + y
                lo = y - (hi - x)
                if lo:
                    break
            if n > 0 and ((lo < 0 and p[n - 1] < 0) or (lo > 0 and p[n - 1] > 0)):
                y = lo * 2
                x = hi + y
                if y == x - hi:
                    hi = x
        return hi

    def __float__(self) -> float:
        return self.valueOf()


def fsum(
    values: Iterable[Any],
    valueof: Callable[[Any, int, Iterable[Any]], Any] | None = None,
) -> float:
    """Return a full-precision floating point sum.

    Mirrors `d3.fsum(values[, valueof])`.
    """

    adder = Adder()
    if valueof is None:
        for v in values:
            x = tonumber(v)
            if x and not math.isnan(x):
                adder.add(x)
    else:
        index = -1
        for v in values:
            index += 1
            x = tonumber(valueof(v, index, values))
            if x and not math.isnan(x):
                adder.add(x)
    return float(adder)


def fcumsum(
    values: Iterable[Any],
    valueof: Callable[[Any, int, Iterable[Any]], Any] | None = None,
) -> list[float]:
    """Return the cumulative sum using full-precision accumulation.

    Mirrors `d3.fcumsum(values[, valueof])`.
    """

    adder = Adder()
    out: list[float] = []
    if valueof is None:
        for v in values:
            x = tonumber(v)
            if x != x:
                x = 0.0
            adder.add(x)
            out.append(float(adder))
    else:
        index = -1
        for v in values:
            index += 1
            x = tonumber(valueof(v, index, values))
            if x != x:
                x = 0.0
            adder.add(x)
            out.append(float(adder))
    return out


__all__ = ["Adder", "fsum", "fcumsum"]
