"""Spherical / numeric helpers (d3-geo `math.js`)."""

from __future__ import annotations

import math

epsilon = 1e-6
epsilon2 = 1e-12
pi = math.pi
halfPi = pi / 2
quarterPi = pi / 4
tau = pi * 2
degrees = 180 / pi
radians = pi / 180


def acos(x: float) -> float:
    return 0 if x > 1 else pi if x < -1 else math.acos(x)


def asin(x: float) -> float:
    return halfPi if x > 1 else -halfPi if x < -1 else math.asin(x)


def haversin(x: float) -> float:
    x = math.sin(x / 2)
    return x * x


def sign(x: float) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0
