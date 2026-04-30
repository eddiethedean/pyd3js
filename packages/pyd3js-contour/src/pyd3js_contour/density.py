"""Contour density — Python port of d3-contour density.js."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from pyd3js_array import blur2, max as max_array, ticks

from pyd3js_contour._constant import constant
from pyd3js_contour.contours import contours as contours_factory

__all__ = ["contourDensity"]

# Matches JS `Number.MIN_VALUE` (~5e-324), used as ticks domain low bound like upstream density.js
_MIN_VALUE = math.ldexp(1.0, -1074)


def _default_x(d: Any, _i: int, _data: Any) -> float:
    return float(d[0])


def _default_y(d: Any, _i: int, _data: Any) -> float:
    return float(d[1])


def _default_weight(_d: Any, _i: int, _data: Any) -> float:
    return 1.0


def _call_accessor(
    fn: Callable[..., Any],
    d: Any,
    i: int,
    data: Sequence[Any],
) -> Any:
    """Match JS: callers may provide unary accessors `(d) => ...`."""

    try:
        return fn(d, i, data)
    except TypeError:
        return fn(d)


class ContourDensityGen:
    """Instance returned by `contourDensity()`."""

    __slots__ = (
        "_x",
        "_y",
        "_weight",
        "_dx",
        "_dy",
        "_r",
        "_k",
        "_threshold",
    )

    def __init__(self) -> None:
        self._x: Callable[..., float] = _default_x
        self._y: Callable[..., float] = _default_y
        self._weight: Callable[..., float] = _default_weight
        self._dx = 960
        self._dy = 500
        self._r = 20.0
        self._k = 2
        self._threshold: Callable[..., Any] = constant(20)

    def _grid_o(self) -> float:
        return self._r * 3.0

    def _n_m(self) -> tuple[int, int]:
        o = self._grid_o()
        n = int(self._dx + o * 2.0) >> self._k
        m = int(self._dy + o * 2.0) >> self._k
        return n, m

    def _resize(self) -> ContourDensityGen:
        return self

    def x(self, f: Any | None = None) -> Any:
        if f is None:
            return self._x
        if callable(f):
            self._x = f
        else:
            self._x = constant(float(f))
        return self

    def y(self, f: Any | None = None) -> Any:
        if f is None:
            return self._y
        if callable(f):
            self._y = f
        else:
            self._y = constant(float(f))
        return self

    def weight(self, f: Any | None = None) -> Any:
        if f is None:
            return self._weight
        if callable(f):
            self._weight = f
        else:
            self._weight = constant(float(f))
        return self

    def size(self, s: Any | None = None) -> Any:
        if s is None:
            return [self._dx, self._dy]
        _0 = float(s[0])
        _1 = float(s[1])
        if not (_0 >= 0 and _1 >= 0):
            raise ValueError("invalid size")
        self._dx = _0
        self._dy = _1
        return self._resize()

    def cellSize(self, sz: float | None = None) -> Any:  # noqa: N802 - match JS name
        if sz is None:
            return 1 << self._k
        if not (float(sz) >= 1):
            raise ValueError("invalid cell size")
        self._k = int(math.floor(math.log(float(sz)) / math.log(2.0)))
        return self._resize()

    def thresholds(self, t: Any | None = None) -> Any:
        if t is None:
            return self._threshold
        if callable(t):
            self._threshold = t
        elif isinstance(t, list):
            self._threshold = constant(list(t))
        else:
            self._threshold = constant(t)
        return self

    def bandwidth(self, b: float | None = None) -> Any:
        if b is None:
            r = self._r
            return math.sqrt(r * (r + 1.0))
        if not (float(b) >= 0):
            raise ValueError("invalid bandwidth")
        bw = float(b)
        self._r = (math.sqrt(4 * bw * bw + 1.0) - 1.0) / 2.0
        return self._resize()

    def _grid(self, data: Sequence[Any]) -> list[float]:
        n, m = self._n_m()
        values = [0.0] * (n * m)
        k = self._k
        pow2k = math.pow(2.0, -k)
        o = self._grid_o()
        i = -1
        for d in data:
            i += 1
            xi = (_call_accessor(self._x, d, i, data) + o) * pow2k
            yi = (_call_accessor(self._y, d, i, data) + o) * pow2k
            try:
                wi = float(_call_accessor(self._weight, d, i, data))
            except (TypeError, ValueError):
                wi = float("nan")
            if math.isnan(wi) or wi == 0.0:
                continue
            if xi >= 0 and xi < n and yi >= 0 and yi < m:
                x0 = int(math.floor(xi))
                y0 = int(math.floor(yi))
                xt = xi - x0 - 0.5
                yt = yi - y0 - 0.5
                base = x0 + y0 * n
                values[base] += (1.0 - xt) * (1.0 - yt) * wi
                values[base + 1] += xt * (1.0 - yt) * wi
                values[base + 1 + n] += xt * yt * wi
                values[base + n] += (1.0 - xt) * yt * wi

        blur2(
            {"data": values, "width": n, "height": m},
            self._r * pow2k,
        )
        return values

    def _transform(self, geometry: dict[str, Any]) -> dict[str, Any]:
        pow2k = math.pow(2.0, self._k)
        o = self._grid_o()
        for poly in geometry["coordinates"]:
            for ring in poly:
                for pt in ring:
                    pt[0] = pt[0] * pow2k - o
                    pt[1] = pt[1] * pow2k - o
        return geometry

    def __call__(self, data: Sequence[Any]) -> list[dict[str, Any]]:
        values = self._grid(data)
        tz_any = self._threshold(values)
        k = self._k
        pow4k = math.pow(2.0, 2 * k)
        if not isinstance(tz_any, list):
            mx = max_array(values)
            if mx is None:
                tz_list = []
            else:
                hi = float(mx) / pow4k
                if hi <= 0:
                    tz_list = []
                else:
                    tz_list = ticks(_MIN_VALUE, hi, float(tz_any))
        else:
            tz_list = [float(x) for x in tz_any]

        tz_levels = [float(t) for t in tz_list]

        n, m = self._n_m()
        gen = contours_factory().size([n, m]).thresholds([t * pow4k for t in tz_levels])
        out = gen(values)
        result: list[dict[str, Any]] = []
        for i, item in enumerate(out):
            item = self._transform(dict(item))
            item["value"] = tz_levels[i]
            result.append(item)
        return result

    def contours(self, data: Sequence[Any]) -> Callable[..., Any]:
        values = self._grid(data)
        k = self._k
        pow4k = math.pow(2.0, 2 * k)
        n, m = self._n_m()
        gen = contours_factory().size([n, m])

        def contour_fn(value: float) -> dict[str, Any]:
            v = float(value)
            c = gen.contour(values, v * pow4k)
            c = self._transform(dict(c))
            c["value"] = v
            return c

        mx = max_array(values)

        class _ContourCallable:
            __slots__ = ()

            def __call__(_self, value: float) -> dict[str, Any]:
                return contour_fn(value)

            @property
            def max(self) -> float:  # noqa: A003 - match JS API
                if mx is None:
                    return 0.0
                return float(mx) / pow4k

        return _ContourCallable()


def contourDensity() -> ContourDensityGen:
    """Create a contour density estimator (mirrors `d3.contourDensity`)."""

    return ContourDensityGen()
