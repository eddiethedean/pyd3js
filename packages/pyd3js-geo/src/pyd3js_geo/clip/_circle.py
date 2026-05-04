"""Clip to small circle (d3-geo `clip/circle.js`)."""

from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_geo._circle_geo import circle_stream
from pyd3js_geo._point_equal import point_equal
from pyd3js_geo.cartesian import (
    cartesian,
    cartesian_add_in_place,
    cartesian_cross,
    cartesian_dot,
    cartesian_scale,
    spherical,
)
from pyd3js_geo.clip._clip import clip

epsilon = 1e-6
pi = math.pi
radians = math.pi / 180


def _abs(x: float) -> float:
    return abs(x)


def clip_circle(radius: float) -> Callable[[Any], Any]:
    cr = math.cos(radius)
    delta = 6 * radians
    small_radius = cr > 0
    not_hemisphere = _abs(cr) > epsilon

    def interpolate(
        from_: list[float] | None,
        to: list[float] | None,
        direction: float,
        stream: Any,
    ) -> None:
        circle_stream(stream, radius, delta, direction, from_, to)

    def visible(lam: float, phi: float) -> bool:
        return math.cos(lam) * math.cos(phi) > cr

    def clip_line(stream: Any) -> dict[str, Callable[..., Any]]:
        point0: list[float] | None = None
        c0 = 0
        v0 = False
        v00 = False
        clean = 1

        def line_start() -> None:
            nonlocal v00, v0, clean, point0
            v00 = v0 = False
            clean = 1
            point0 = None

        def code(lam: float, phi: float) -> int:
            r = radius if small_radius else pi - radius
            c = 0
            if lam < -r:
                c |= 1
            elif lam > r:
                c |= 2
            if phi < -r:
                c |= 4
            elif phi > r:
                c |= 8
            return c

        def intersect(a: list[float], b: list[float], two: bool = False):
            pa = cartesian(a)
            pb = cartesian(b)
            n1 = [1.0, 0.0, 0.0]
            n2 = cartesian_cross(pa, pb)
            n2n2 = cartesian_dot(n2, n2)
            n1n2 = n2[0]
            determinant = n2n2 - n1n2 * n1n2
            if not determinant:
                return None if two else a  # pragma: no cover

            c1 = cr * n2n2 / determinant
            c2 = -cr * n1n2 / determinant
            n1xn2 = cartesian_cross(n1, n2)
            a_vec = cartesian_scale(n1, c1)
            b_vec = cartesian_scale(n2, c2)
            cartesian_add_in_place(a_vec, b_vec)

            u = n1xn2
            w = cartesian_dot(a_vec, u)
            uu = cartesian_dot(u, u)
            t2 = w * w - uu * (cartesian_dot(a_vec, a_vec) - 1)
            if t2 < 0:
                return None
            t = math.sqrt(t2)
            q = cartesian_scale(u, (-w - t) / uu)
            cartesian_add_in_place(q, a_vec)
            q = spherical(q)

            if not two:
                return q

            lambda0, lambda1 = a[0], b[0]
            phi0, phi1 = a[1], b[1]
            if lambda1 < lambda0:
                lambda0, lambda1 = lambda1, lambda0
            delta_l = lambda1 - lambda0
            polar = _abs(delta_l - pi) < epsilon
            meridian = polar or delta_l < epsilon
            if not polar and phi1 < phi0:
                phi0, phi1 = phi1, phi0

            q1 = cartesian_scale(u, (-w + t) / uu)
            cartesian_add_in_place(q1, a_vec)
            q1 = spherical(q1)

            if meridian:
                if polar:
                    cond = (phi0 + phi1 > 0) ^ (  # pragma: no cover
                        q[1] < (phi0 if _abs(q[0] - lambda0) < epsilon else phi1)
                    )
                else:
                    cond = phi0 <= q[1] <= phi1
            else:
                cond = (delta_l > pi) ^ (lambda0 <= q[0] <= lambda1)

            if cond:
                return [q, q1]  # pragma: no cover
            return None

        def point(lam: float, phi: float) -> None:
            nonlocal point0, c0, v0, v00, clean
            point1 = [lam, phi]
            v = visible(lam, phi)
            if small_radius:
                c = 0 if v else code(lam, phi)
            else:
                c = 0 if not v else code(lam + (pi if lam < 0 else -pi), phi)

            if not point0:
                v00 = v0 = v
                if v:
                    stream.lineStart()

            if v != v0 and point0 is not None:
                p2t = intersect(point0, point1)
                if not p2t or point_equal(point0, p2t) or point_equal(point1, p2t):
                    point1.append(1.0)  # pragma: no cover
            if v != v0:
                clean = 0
                if v:
                    stream.lineStart()
                    point2 = intersect(point1, point0) if point0 is not None else None
                    if point2 is not None:
                        stream.point(point2[0], point2[1])
                else:
                    point2 = intersect(point0, point1) if point0 is not None else None
                    if point2 is not None:
                        stream.point(point2[0], point2[1], 2)
                    stream.lineEnd()
                point0 = point2
            elif not_hemisphere and point0 is not None and (small_radius ^ v):
                t = intersect(point1, point0, True) if not (c & c0) else None
                if t:
                    clean = 0  # pragma: no cover
                    if small_radius:  # pragma: no cover
                        stream.lineStart()  # pragma: no cover
                        stream.point(t[0][0], t[0][1])  # pragma: no cover
                        stream.point(t[1][0], t[1][1])  # pragma: no cover
                        stream.lineEnd()  # pragma: no cover
                    else:
                        stream.point(t[1][0], t[1][1])  # pragma: no cover
                        stream.lineEnd()  # pragma: no cover
                        stream.lineStart()  # pragma: no cover
                        stream.point(t[0][0], t[0][1], 3)  # pragma: no cover
            if v and (point0 is None or not point_equal(point0, point1)):
                if len(point1) > 2:
                    stream.point(point1[0], point1[1], point1[2])  # pragma: no cover
                else:
                    stream.point(point1[0], point1[1])
            point0, v0, c0 = point1, v, c

        def line_end() -> None:
            nonlocal point0, v0
            if v0:
                stream.lineEnd()
            point0 = None

        def clean_fn() -> int:
            return clean | ((v00 and v0) << 1)

        return {
            "lineStart": line_start,
            "point": point,
            "lineEnd": line_end,
            "clean": clean_fn,
        }

    start = [0.0, -radius] if small_radius else [-pi, radius - pi]
    return clip(visible, clip_line, interpolate, start)
