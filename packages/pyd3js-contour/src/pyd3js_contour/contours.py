"""Contours factory — Python port of d3-contour contours.js."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from pyd3js_array import extent, nice, thresholdSturges, ticks

from pyd3js_contour._area import area as polygon_area
from pyd3js_contour._constant import constant
from pyd3js_contour._contains import contains

__all__ = ["contours"]


# Marching squares case table (mirrors d3-contour src/contours.js)
_CASES: list[list[list[list[float]]]] = [
    [],
    [[[1.0, 1.5], [0.5, 1.0]]],
    [[[1.5, 1.0], [1.0, 1.5]]],
    [[[1.5, 1.0], [0.5, 1.0]]],
    [[[1.0, 0.5], [1.5, 1.0]]],
    [[[1.0, 1.5], [0.5, 1.0]], [[1.0, 0.5], [1.5, 1.0]]],
    [[[1.0, 0.5], [1.0, 1.5]]],
    [[[1.0, 0.5], [0.5, 1.0]]],
    [[[0.5, 1.0], [1.0, 0.5]]],
    [[[1.0, 1.5], [1.0, 0.5]]],
    [[[0.5, 1.0], [1.0, 0.5]], [[1.5, 1.0], [1.0, 1.5]]],
    [[[1.5, 1.0], [1.0, 0.5]]],
    [[[0.5, 1.0], [1.5, 1.0]]],
    [[[1.0, 1.5], [1.5, 1.0]]],
    [[[0.5, 1.0], [1.0, 1.5]]],
    [],
]


def _finite(x: Any, i: int, values: Sequence[Any]) -> float:
    # Match JS isFinite: null coerces to 0.
    if x is None:
        return 0.0
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v if math.isfinite(v) else float("nan")


def _above(x: Any, value: float) -> bool:
    if x is None:
        return False
    try:
        return float(x) >= value
    except (TypeError, ValueError):
        return False


def _valid(v: Any) -> float:
    if v is None:
        return float("-inf")
    try:
        v = float(v)
    except (TypeError, ValueError):
        return float("-inf")
    return v if not math.isnan(v) else float("-inf")


def _smooth1(x: float, v0: float, v1: float, value: float) -> float:
    a = value - v0
    b = v1 - v0
    if math.isfinite(a) or math.isfinite(b):
        # Match JS: 0 / 0 is NaN (Python raises ZeroDivisionError).
        try:
            d = a / b
        except ZeroDivisionError:
            d = float("nan")
    elif a != 0 and b != 0:
        d = math.copysign(1.0, a) / math.copysign(1.0, b)
    else:  # pragma: no cover — no finite (a,b) with both ~0 (mirrors JS fallback)
        d = float("nan")
    return x if math.isnan(d) else x + d - 0.5


class _Fragment:
    __slots__ = ("start", "end", "ring")

    def __init__(self, start: int, end: int, ring: list[list[float]]) -> None:
        self.start = start
        self.end = end
        self.ring = ring


def _index(point: list[float], dx: int) -> int:
    return int(point[0] * 2 + point[1] * (dx + 1) * 4)


class ContoursGen:
    """Instance returned by `contours()` — mirrors d3 `contours` generator."""

    __slots__ = ("_dx", "_dy", "_threshold", "_smooth_linear")

    def __init__(self) -> None:
        self._dx = 1
        self._dy = 1
        self._threshold: Callable[[Sequence[Any]], Any] = thresholdSturges
        self._smooth_linear = True

    def __call__(self, values: Sequence[Any]) -> list[dict[str, Any]]:
        tz_any = self._threshold(values)
        if not isinstance(tz_any, list):
            e = extent(list(values), _finite)
            if e[0] is None or e[1] is None:
                tz_list: list[float] = []
            else:
                e0 = float(e[0])
                e1 = float(e[1])
                count = float(tz_any)
                ns = nice(e0, e1, count)
                tz_list = ticks(ns[0], ns[1], count)
                while tz_list and tz_list[-1] >= e1:
                    tz_list.pop()
                while len(tz_list) > 1 and tz_list[1] < e0:
                    tz_list.pop(0)
        else:
            tz_list = sorted(float(x) for x in tz_any)

        return [self.contour(values, value) for value in tz_list]

    def contour(self, values: Sequence[Any], value: Any) -> dict[str, Any]:
        try:
            v = float("nan") if value is None else float(value)
        except (TypeError, ValueError):
            raise ValueError(f"invalid value: {value}") from None
        if math.isnan(v):
            raise ValueError(f"invalid value: {value}")

        polygons: list[list[list[list[float]]]] = []
        holes: list[list[list[float]]] = []

        def callback(ring: list[list[float]]) -> None:
            if self._smooth_linear:
                self._smooth_linear_ring(ring, values, v)
            if polygon_area(ring) > 0:
                polygons.append([ring])
            else:
                holes.append(ring)

        self._isorings(values, v, callback)

        for hole in holes:
            for i in range(len(polygons)):
                polygon = polygons[i]
                if contains(polygon[0], hole) != -1:
                    polygon.append(hole)
                    break

        return {"type": "MultiPolygon", "value": value, "coordinates": polygons}

    def size(self, s: Any | None = None) -> Any:
        if s is None:
            return [self._dx, self._dy]
        _0 = int(math.floor(float(s[0])))
        _1 = int(math.floor(float(s[1])))
        if not (_0 >= 0 and _1 >= 0):
            raise ValueError("invalid size")
        self._dx = _0
        self._dy = _1
        return self

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

    def smooth(self, s: Any | None = None) -> Any:
        if s is None:
            return self._smooth_linear
        self._smooth_linear = bool(s)
        return self

    def _smooth_linear_ring(
        self,
        ring: list[list[float]],
        values: Sequence[Any],
        value: float,
    ) -> None:
        dx = self._dx
        dy = self._dy
        for point in ring:
            xf = point[0]
            yf = point[1]
            xt = int(xf) | 0
            yt = int(yf) | 0
            idx = yt * dx + xt
            v1 = _valid(values[idx]) if idx < len(values) else float("-inf")
            if xf > 0 and xf < dx and xf == float(xt):
                li = yt * dx + xt - 1
                left = _valid(values[li]) if li < len(values) else float("-inf")
                point[0] = _smooth1(xf, left, v1, value)
            if yf > 0 and yf < dy and yf == float(yt):
                ui = (yt - 1) * dx + xt
                up = _valid(values[ui]) if ui < len(values) else float("-inf")
                point[1] = _smooth1(yf, up, v1, value)

    def _isorings(
        self,
        values: Sequence[Any],
        value: float,
        callback: Callable[[list[list[float]]], None],
    ) -> None:
        dx = self._dx
        dy = self._dy
        fragment_by_start: dict[int, _Fragment] = {}
        fragment_by_end: dict[int, _Fragment] = {}

        def stitch(line: list[list[float]]) -> None:
            start = [line[0][0] + xi, line[0][1] + yi]
            end = [line[1][0] + xi, line[1][1] + yi]
            start_index = _index(start, dx)
            end_index = _index(end, dx)
            f = fragment_by_end.get(start_index)
            if f is not None:
                g = fragment_by_start.get(end_index)
                if g is not None:
                    del fragment_by_end[f.end]
                    del fragment_by_start[g.start]
                    if f is g:
                        f.ring.append(end)
                        callback(f.ring)
                    else:
                        fragment_by_start[f.start] = fragment_by_end[g.end] = _Fragment(
                            f.start,
                            g.end,
                            f.ring + g.ring,
                        )
                else:
                    del fragment_by_end[f.end]
                    f.ring.append(end)
                    f.end = end_index
                    fragment_by_end[f.end] = f
            else:
                f = fragment_by_start.get(end_index)
                if f is not None:
                    g = fragment_by_end.get(start_index)
                    if g is not None:  # pragma: no cover — never observed in grid tests; d3 stitch.js parity
                        del fragment_by_start[f.start]
                        del fragment_by_end[g.end]
                        if f is g:
                            f.ring.append(end)
                            callback(f.ring)
                        else:
                            fragment_by_start[g.start] = fragment_by_end[f.end] = _Fragment(
                                g.start,
                                f.end,
                                g.ring + f.ring,
                            )
                    else:
                        del fragment_by_start[f.start]
                        f.ring.insert(0, start)
                        f.start = start_index
                        fragment_by_start[f.start] = f
                else:
                    frag = _Fragment(start_index, end_index, [start, end])
                    fragment_by_start[start_index] = frag
                    fragment_by_end[end_index] = frag

        # First row (y = -1)
        xi = yi = -1
        t1 = _above(values[0], value) if len(values) > 0 else False
        for seg in _CASES[(int(t1) << 1)]:
            stitch([list(p) for p in seg])
        xi = -1
        while True:
            xi += 1
            if xi >= dx - 1:
                break
            t0 = t1
            t1 = _above(values[xi + 1], value) if xi + 1 < len(values) else False
            for seg in _CASES[int(t0) | int(t1) << 1]:
                stitch([list(p) for p in seg])
        for seg in _CASES[int(t1) << 0]:
            stitch([list(p) for p in seg])

        # Intermediate rows (JS: while (++y < dy - 1)); yi runs -1 then 0..dy-2 in body
        yi = -1
        while True:
            yi += 1
            if yi >= dy - 1:
                break
            xi = -1
            row = yi * dx
            t1 = _above(values[row + dx], value) if row + dx < len(values) else False
            t2 = _above(values[row], value) if row < len(values) else False
            for seg in _CASES[int(t1) << 1 | int(t2) << 2]:
                stitch([list(p) for p in seg])
            xi = -1
            while True:
                xi += 1
                if xi >= dx - 1:
                    break
                t0 = t1
                t1 = (
                    _above(values[row + dx + xi + 1], value)
                    if row + dx + xi + 1 < len(values)
                    else False
                )
                t3 = t2
                t2 = (
                    _above(values[row + xi + 1], value)
                    if row + xi + 1 < len(values)
                    else False
                )
                for seg in _CASES[int(t0) | int(t1) << 1 | int(t2) << 2 | int(t3) << 3]:
                    stitch([list(p) for p in seg])
            for seg in _CASES[int(t1) | int(t2) << 3]:
                stitch([list(p) for p in seg])

        # Last row (y = dy - 1) — JS uses `values[row] >= value` (null coerces via `ToNumber`)
        xi = -1
        row = yi * dx

        def _last_row_ge(idx: int, thresh: float) -> bool:
            if idx < 0 or idx >= len(values):
                return False
            vr = values[idx]
            if vr is None:
                num = 0.0  # JS: +null === 0
            else:
                try:
                    num = float(vr)
                except (TypeError, ValueError):
                    return False
            return not math.isnan(num) and num >= thresh

        t2 = _last_row_ge(row, value)
        for seg in _CASES[int(t2) << 2]:
            stitch([list(p) for p in seg])
        xi = -1
        while True:
            xi += 1
            if xi >= dx - 1:
                break
            t3 = t2
            t2 = (
                _above(values[row + xi + 1], value)
                if row + xi + 1 < len(values)
                else False
            )
            for seg in _CASES[int(t2) << 2 | int(t3) << 3]:
                stitch([list(p) for p in seg])
        for seg in _CASES[int(t2) << 3]:
            stitch([list(p) for p in seg])


def contours() -> ContoursGen:
    """Create a new contours generator (mirrors `d3.contours`)."""

    return ContoursGen()
