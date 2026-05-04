"""Spherical polygon containment (d3-geo `polygonContains.js`)."""

from __future__ import annotations

import math
from typing import Any, Sequence

from pyd3js_array import Adder

from pyd3js_geo.cartesian import (
    cartesian,
    cartesian_cross,
    cartesian_normalize_in_place,
)
from pyd3js_geo.math import radians

epsilon = 1e-6
epsilon2 = 1e-12
half_pi = math.pi / 2
quarter_pi = math.pi / 4
pi = math.pi
tau = 2 * math.pi


def _sign(x: float) -> float:
    return 1.0 if x > 0 else -1.0 if x < 0 else 0.0


def _longitude(point: Sequence[float]) -> float:
    x = point[0]
    return x if abs(x) <= pi else _sign(x) * ((abs(x) + pi) % tau - pi)


def polygon_contains_rings(
    polygon: list[list[list[float]]], point: Sequence[float]
) -> bool:
    """Rings and point are in radians (lambda, phi)."""
    lam = _longitude(point)
    phi = point[1]
    sin_phi = math.sin(phi)
    normal = [math.sin(lam), -math.cos(lam), 0.0]
    angle = 0.0
    winding = 0

    sum_ = Adder()

    if sin_phi == 1:
        phi = half_pi + epsilon
    elif sin_phi == -1:
        phi = -half_pi - epsilon

    for ring in polygon:
        m = len(ring)
        if not m:
            continue
        point0 = ring[m - 1]
        lam0 = _longitude(point0)
        phi0_h = point0[1] / 2 + quarter_pi
        sin_phi0 = math.sin(phi0_h)
        cos_phi0 = math.cos(phi0_h)

        j = 0
        while j < m:
            point1 = ring[j]
            lam1 = _longitude(point1)
            phi1_h = point1[1] / 2 + quarter_pi
            sin_phi1 = math.sin(phi1_h)
            cos_phi1 = math.cos(phi1_h)
            delta = lam1 - lam0
            sgn = 1.0 if delta >= 0 else -1.0
            abs_delta = sgn * delta
            antimeridian = abs_delta > pi
            k = sin_phi0 * sin_phi1

            sum_.add(
                math.atan2(
                    k * sgn * math.sin(abs_delta),
                    cos_phi0 * cos_phi1 + k * math.cos(abs_delta),
                )
            )
            angle += (delta + sgn * tau) if antimeridian else delta

            # (antimeridian ^ ((lambda0 >= lambda) ^ (lambda1 >= lambda)))
            if antimeridian ^ ((lam0 >= lam) ^ (lam1 >= lam)):
                arc = cartesian_cross(cartesian(point0), cartesian(point1))
                cartesian_normalize_in_place(arc)
                intersection = cartesian_cross(normal, arc)
                cartesian_normalize_in_place(intersection)
                phi_arc = (-1.0 if (antimeridian ^ (delta >= 0)) else 1.0) * math.asin(
                    intersection[2]
                )
                if phi > phi_arc or (phi == phi_arc and (arc[0] != 0 or arc[1] != 0)):
                    winding += 1 if (antimeridian ^ (delta >= 0)) else -1

            lam0 = lam1
            sin_phi0 = sin_phi1
            cos_phi0 = cos_phi1
            point0 = point1
            j += 1

    return bool(
        (angle < -epsilon or (angle < epsilon and float(sum_) < -epsilon2))
        ^ (winding & 1)
    )


def polygon_contains_degrees(polygon: Any, point: Any) -> bool:
    """Spherical polygon containment with rings and point in degrees (d3 test harness).

    `polygon` is a list of rings; each ring is a list of ``[lon, lat]`` in degrees
    (ints or floats). `point` is ``[lon, lat]`` in degrees.

    Matches d3-geo `polygonContains-test.js`: each ring is converted to radians and
    the duplicate closing vertex is removed, like ``ring.map(radians); ring.pop()``.
    """

    rings_rad: list[list[list[float]]] = []
    for ring in polygon:
        r = [[float(p[0]) * radians, float(p[1]) * radians] for p in ring]
        if r:
            r = r[:-1]
        rings_rad.append(r)
    pt = (float(point[0]) * radians, float(point[1]) * radians)
    return polygon_contains_rings(rings_rad, pt)
