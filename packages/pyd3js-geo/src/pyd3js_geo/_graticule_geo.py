"""geoGraticule (d3-geo `graticule.js`)."""

from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_array import range as d3range

epsilon = 1e-6


def _abs(x: float) -> float:
    return abs(x)


def _ceil(x: float) -> float:
    return math.ceil(x)


def graticule_x(
    y0: float, y1: float, dy: float
) -> Callable[[float], list[list[float]]]:
    y = list(d3range(_ceil(y0 / dy) * dy, y1 - epsilon, dy)) + [y1]

    def fx(x: float) -> list[list[float]]:
        return [[x, yi] for yi in y]

    return fx


def graticule_y(
    x0: float, x1: float, dx: float
) -> Callable[[float], list[list[float]]]:
    x = list(d3range(_ceil(x0 / dx) * dx, x1 - epsilon, dx)) + [x1]

    def fy(y: float) -> list[list[float]]:
        return [[xi, y] for xi in x]

    return fy


_MISSING = object()


def geo_graticule_factory() -> Any:
    x1 = y1 = X1 = Y1 = 0.0
    x0 = y0 = X0 = Y0 = 0.0
    dx = 10.0
    dy = 10.0
    DX = 90.0
    DY = 360.0
    x_fn: Callable[[float], list[list[float]]] | None = None
    y_fn: Callable[[float], list[list[float]]] | None = None
    X_fn: Callable[[float], list[list[float]]] | None = None
    Y_fn: Callable[[float], list[list[float]]] | None = None
    precision = 2.5

    def graticule(*_a: Any, **_k: Any) -> dict[str, Any]:
        return {"type": "MultiLineString", "coordinates": lines()}

    def lines() -> list[list[list[float]]]:
        assert (
            x_fn is not None
            and y_fn is not None
            and X_fn is not None
            and Y_fn is not None
        )
        lo_x = list(d3range(_ceil(X0 / DX) * DX, X1, DX))
        lo_y = list(d3range(_ceil(Y0 / DY) * DY, Y1, DY))
        mi_x = [
            xx for xx in d3range(_ceil(x0 / dx) * dx, x1, dx) if _abs(xx % DX) > epsilon
        ]
        mi_y = [
            yy for yy in d3range(_ceil(y0 / dy) * dy, y1, dy) if _abs(yy % DY) > epsilon
        ]
        out: list[list[list[float]]] = []
        for v in lo_x:
            out.append(X_fn(v))
        for v in lo_y:
            out.append(Y_fn(v))
        for v in mi_x:
            out.append(x_fn(v))
        for v in mi_y:
            out.append(y_fn(v))
        return out

    def lines_feat() -> list[dict[str, Any]]:
        return [{"type": "LineString", "coordinates": c} for c in lines()]

    def outline() -> dict[str, Any]:
        assert X_fn is not None and Y_fn is not None
        seg = (
            X_fn(X0)
            + Y_fn(Y1)[1:]
            + list(reversed(X_fn(X1)))[1:]
            + list(reversed(Y_fn(Y0)))[1:]
        )
        return {"type": "Polygon", "coordinates": [seg]}

    def extent_major(ext: Any = _MISSING) -> Any:
        nonlocal X0, X1, Y0, Y1
        if ext is _MISSING:
            return [[X0, Y0], [X1, Y1]]
        X0, X1 = float(ext[0][0]), float(ext[1][0])
        Y0, Y1 = float(ext[0][1]), float(ext[1][1])
        if X0 > X1:
            X0, X1 = X1, X0
        if Y0 > Y1:
            Y0, Y1 = Y1, Y0
        return precision_fn(precision)

    def extent_minor(ext: Any = _MISSING) -> Any:
        nonlocal x0, x1, y0, y1
        if ext is _MISSING:
            return [[x0, y0], [x1, y1]]
        x0, x1 = float(ext[0][0]), float(ext[1][0])
        y0, y1 = float(ext[0][1]), float(ext[1][1])
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        return precision_fn(precision)

    def extent_both(ext: Any = _MISSING) -> Any:
        if ext is _MISSING:
            return extent_minor()
        extent_major(ext)
        return extent_minor(ext)

    def step_major(st: Any = _MISSING) -> Any:
        nonlocal DX, DY
        if st is _MISSING:
            return [DX, DY]
        DX, DY = float(st[0]), float(st[1])
        return graticule

    def step_minor(st: Any = _MISSING) -> Any:
        nonlocal dx, dy
        if st is _MISSING:
            return [dx, dy]
        dx, dy = float(st[0]), float(st[1])
        return graticule

    def step_both(st: Any = _MISSING) -> Any:
        if st is _MISSING:
            return step_minor()
        step_major(st)
        return step_minor(st)

    def precision_fn(pr: Any = _MISSING) -> Any:
        nonlocal precision, x_fn, y_fn, X_fn, Y_fn
        if pr is _MISSING:
            return precision
        precision = float(pr)
        # d3-geo: x = graticuleX(y0, y1, dx); X = graticuleX(Y0, Y1, DX)
        x_fn = graticule_x(y0, y1, dx)
        y_fn = graticule_y(x0, x1, precision)
        X_fn = graticule_x(Y0, Y1, DX)
        Y_fn = graticule_y(X0, X1, precision)
        return graticule

    graticule.lines = lines_feat  # type: ignore[attr-defined]
    graticule.outline = outline  # type: ignore[attr-defined]
    graticule.extent = extent_both  # type: ignore[attr-defined]
    graticule.extentMajor = extent_major  # type: ignore[attr-defined]
    graticule.extentMinor = extent_minor  # type: ignore[attr-defined]
    graticule.step = step_both  # type: ignore[attr-defined]
    graticule.stepMajor = step_major  # type: ignore[attr-defined]
    graticule.stepMinor = step_minor  # type: ignore[attr-defined]
    graticule.precision = precision_fn  # type: ignore[attr-defined]

    graticule.extentMajor([[-180, -90 + epsilon], [180, 90 - epsilon]])
    graticule.extentMinor([[-180, -80 - epsilon], [180, 80 + epsilon]])
    return graticule
