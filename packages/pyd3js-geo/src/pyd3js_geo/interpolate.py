"""Great-circle interpolation (d3-geo `interpolate.js`)."""

from __future__ import annotations

import math

from pyd3js_geo.math import asin, degrees, haversin, radians


def geoInterpolate(a: list[float], b: list[float]):
    x0, y0, x1, y1 = a[0] * radians, a[1] * radians, b[0] * radians, b[1] * radians
    cy0, sy0, cy1, sy1 = math.cos(y0), math.sin(y0), math.cos(y1), math.sin(y1)
    kx0, ky0, kx1, ky1 = (
        cy0 * math.cos(x0),
        cy0 * math.sin(x0),
        cy1 * math.cos(x1),
        cy1 * math.sin(x1),
    )
    d = 2 * asin(math.sqrt(haversin(y1 - y0) + cy0 * cy1 * haversin(x1 - x0)))
    k = math.sin(d)
    if d:

        def interpolate(t: float) -> list[float]:
            t *= d
            B, A = math.sin(t) / k, math.sin(d - t) / k
            x, y, z = A * kx0 + B * kx1, A * ky0 + B * ky1, A * sy0 + B * sy1
            return [
                math.atan2(y, x) * degrees,
                math.atan2(z, math.sqrt(x * x + y * y)) * degrees,
            ]

    else:

        def interpolate(t: float = 0) -> list[float]:
            return [x0 * degrees, y0 * degrees]

    interpolate.distance = d  # type: ignore[attr-defined]
    return interpolate
