"""Spherical rotation (d3-geo `rotation.js`)."""

from __future__ import annotations

import math
from typing import Callable

from pyd3js_geo.compose import compose
from pyd3js_geo.math import asin, degrees, pi, radians, tau


def rotationIdentity(lambda_: float, phi: float) -> list[float]:
    if abs(lambda_) > pi:
        lambda_ -= round(lambda_ / tau) * tau
    return [lambda_, phi]


rotationIdentity.invert = rotationIdentity  # type: ignore[attr-defined]


def _forward_rotation_lambda(
    delta_lambda: float,
) -> Callable[[float, float], list[float]]:
    def rotation(lambda_: float, phi: float) -> list[float]:
        lambda_ += delta_lambda
        if abs(lambda_) > pi:
            lambda_ -= round(lambda_ / tau) * tau
        return [lambda_, phi]

    return rotation


def _rotation_lambda(delta_lambda: float) -> Callable[[float, float], list[float]]:
    rotation = _forward_rotation_lambda(delta_lambda)
    rotation.invert = _forward_rotation_lambda(-delta_lambda)  # type: ignore[attr-defined]
    return rotation


def _rotation_phi_gamma(
    delta_phi: float, delta_gamma: float
) -> Callable[[float, float], list[float]]:
    cdp, sdp = math.cos(delta_phi), math.sin(delta_phi)
    cdg, sdg = math.cos(delta_gamma), math.sin(delta_gamma)

    def rotation(lambda_: float, phi: float) -> list[float]:
        cp = math.cos(phi)
        x, y, z = math.cos(lambda_) * cp, math.sin(lambda_) * cp, math.sin(phi)
        k = z * cdp + x * sdp
        return [
            math.atan2(y * cdg - k * sdg, x * cdp - z * sdp),
            asin(k * cdg + y * sdg),
        ]

    def invert(lambda_: float, phi: float) -> list[float]:
        cp = math.cos(phi)
        x, y, z = math.cos(lambda_) * cp, math.sin(lambda_) * cp, math.sin(phi)
        k = z * cdg - y * sdg
        return [
            math.atan2(y * cdg + z * sdg, x * cdp + k * sdp),
            asin(k * cdp - x * sdp),
        ]

    rotation.invert = invert  # type: ignore[attr-defined]
    return rotation


def rotateRadians(
    delta_lambda: float, delta_phi: float, delta_gamma: float
) -> Callable[[float, float], list[float]]:
    delta_lambda = math.fmod(delta_lambda, tau)
    if delta_lambda:
        return (
            compose(
                _rotation_lambda(delta_lambda),
                _rotation_phi_gamma(delta_phi, delta_gamma),
            )
            if delta_phi or delta_gamma
            else _rotation_lambda(delta_lambda)
        )
    return (
        _rotation_phi_gamma(delta_phi, delta_gamma)
        if delta_phi or delta_gamma
        else rotationIdentity
    )


def geoRotation(rotate: list[float]) -> Callable[[list[float]], list[float]]:
    rot = rotateRadians(
        rotate[0] * radians,
        rotate[1] * radians,
        (rotate[2] if len(rotate) > 2 else 0) * radians,
    )

    def forward(coordinates: list[float]) -> list[float]:
        c = rot(coordinates[0] * radians, coordinates[1] * radians)
        return [c[0] * degrees, c[1] * degrees]

    def invert(coordinates: list[float]) -> list[float]:
        c = rot.invert(coordinates[0] * radians, coordinates[1] * radians)  # type: ignore[attr-defined]
        return [c[0] * degrees, c[1] * degrees]

    forward.invert = invert  # type: ignore[attr-defined]
    return forward
