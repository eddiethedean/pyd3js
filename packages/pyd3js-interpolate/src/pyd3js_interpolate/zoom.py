"""interpolateZoom — port of d3-interpolate `zoom.js`."""

from __future__ import annotations

import math
from collections.abc import Callable


def _cosh(x: float) -> float:
    ex = math.exp(x)
    return (ex + 1.0 / ex) / 2.0


def _sinh(x: float) -> float:
    ex = math.exp(x)
    return (ex - 1.0 / ex) / 2.0


def _tanh(x: float) -> float:
    ex = math.exp(2.0 * x)
    return (ex - 1.0) / (ex + 1.0)


def _zoom_rho(
    rho: float, rho2: float, rho4: float
) -> Callable[[list[float], list[float]], Callable[[float], list[float]]]:
    epsilon2 = 1e-12

    def zoom(p0: list[float], p1: list[float]) -> Callable[[float], list[float]]:
        ux0, uy0, w0 = p0[0], p0[1], p0[2]
        ux1, uy1, w1 = p1[0], p1[1], p1[2]
        dx = ux1 - ux0
        dy = uy1 - uy0
        d2 = dx * dx + dy * dy

        if d2 < epsilon2:
            s = math.log(w1 / w0) / rho if w0 != 0 else 0.0

            def i_linear(t: float) -> list[float]:
                return [
                    ux0 + t * dx,
                    uy0 + t * dy,
                    w0 * math.exp(rho * t * s),
                ]

            i_fn: Callable[[float], list[float]] = i_linear
        else:
            d1 = math.sqrt(d2)
            b0 = (w1 * w1 - w0 * w0 + rho4 * d2) / (2 * w0 * rho2 * d1)
            b1 = (w1 * w1 - w0 * w0 - rho4 * d2) / (2 * w1 * rho2 * d1)
            r0 = math.log(math.sqrt(b0 * b0 + 1) - b0)
            r1 = math.log(math.sqrt(b1 * b1 + 1) - b1)
            s = (r1 - r0) / rho

            def i_curve(t: float) -> list[float]:
                st = t * s
                coshr0 = _cosh(r0)
                u = w0 / (rho2 * d1) * (coshr0 * _tanh(rho * st + r0) - _sinh(r0))
                return [
                    ux0 + u * dx,
                    uy0 + u * dy,
                    w0 * coshr0 / _cosh(rho * st + r0),
                ]

            i_fn = i_curve

        duration = s * 1000.0 * rho / math.sqrt(2.0)
        i_fn.duration = duration  # type: ignore[attr-defined]
        return i_fn

    def rho_set(
        r: float,
    ) -> Callable[[list[float], list[float]], Callable[[float], list[float]]]:
        r1 = max(1e-3, float(r))
        r2 = r1 * r1
        r4 = r2 * r2
        return _zoom_rho(r1, r2, r4)

    zoom.rho = rho_set  # type: ignore[attr-defined]
    return zoom


_sqrt2 = math.sqrt(2.0)
interpolate_zoom = _zoom_rho(_sqrt2, 2.0, 4.0)

__all__ = ["interpolate_zoom"]
