"""3D Cartesian helpers for spherical geometry (d3-geo `cartesian.js`)."""

from __future__ import annotations

import math
from typing import Sequence


def spherical(cart: Sequence[float]) -> list[float]:
    return [math.atan2(cart[1], cart[0]), math.asin(cart[2])]


def cartesian(sph: Sequence[float]) -> list[float]:
    lam, phi = sph[0], sph[1]
    cp = math.cos(phi)
    return [cp * math.cos(lam), cp * math.sin(lam), math.sin(phi)]


def cartesian_cross(a: Sequence[float], b: Sequence[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def cartesian_normalize_in_place(d: list[float]) -> None:
    mag = math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])
    if mag == 0:
        return
    d[0] /= mag
    d[1] /= mag
    d[2] /= mag


def cartesian_dot(a: Sequence[float], b: Sequence[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cartesian_scale(a: Sequence[float], k: float) -> list[float]:
    return [a[0] * k, a[1] * k, a[2] * k]


def cartesian_add_in_place(a: list[float], b: Sequence[float]) -> None:
    a[0] += b[0]
    a[1] += b[1]
    a[2] += b[2]
