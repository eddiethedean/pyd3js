"""Clip to antimeridian (d3-geo `clip/antimeridian.js`)."""

from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_geo.clip._clip import clip

epsilon = 1e-6
pi = math.pi
half_pi = pi / 2


def _abs(x: float) -> float:
    return abs(x)


def _sin(x: float) -> float:
    return math.sin(x)


def _atan(x: float) -> float:
    return math.atan(x)


def clip_antimeridian_interpolate(
    from_: list[float] | None,
    to: list[float] | None,
    direction: float,
    stream: Any,
) -> None:
    if from_ is None:
        phi = direction * half_pi
        stream.point(-pi, phi)
        stream.point(0, phi)
        stream.point(pi, phi)
        stream.point(pi, 0)
        stream.point(pi, -phi)
        stream.point(0, -phi)
        stream.point(-pi, -phi)
        stream.point(-pi, 0)
        stream.point(-pi, phi)
    elif _abs(from_[0] - to[0]) > epsilon if to else True:
        assert to is not None
        lam = pi if from_[0] < to[0] else -pi
        phi = direction * lam / 2
        stream.point(-lam, phi)
        stream.point(0, phi)
        stream.point(lam, phi)
    else:
        assert to is not None  # pragma: no cover
        stream.point(to[0], to[1])  # pragma: no cover


def _clip_antimeridian_intersect(
    lambda0: float, phi0: float, lambda1: float, phi1: float
) -> float:
    sin_lambda0_lambda1 = _sin(lambda0 - lambda1)
    if _abs(sin_lambda0_lambda1) > epsilon:
        cos_phi0 = math.cos(phi0)
        cos_phi1 = math.cos(phi1)
        return _atan(
            (
                _sin(phi0) * cos_phi1 * _sin(lambda1)
                - _sin(phi1) * cos_phi0 * _sin(lambda0)
            )
            / (cos_phi0 * cos_phi1 * sin_lambda0_lambda1)
        )
    return (phi0 + phi1) / 2


def clip_antimeridian_line(stream: Any) -> dict[str, Callable[..., Any]]:
    lambda0 = math.nan
    phi0 = math.nan
    sign0 = math.nan
    clean = 1

    def line_start() -> None:
        nonlocal clean
        stream.lineStart()
        clean = 1

    def point(lambda1: float, phi1: float) -> None:
        nonlocal lambda0, phi0, sign0, clean
        sign1 = pi if lambda1 > 0 else -pi
        delta = _abs(lambda1 - lambda0)
        if _abs(delta - pi) < epsilon:
            phi_mid = half_pi if (phi0 + phi1) / 2 > 0 else -half_pi  # pragma: no cover
            stream.point(lambda0, phi_mid)  # pragma: no cover
            stream.point(sign0, phi_mid)  # pragma: no cover
            stream.lineEnd()  # pragma: no cover
            stream.lineStart()  # pragma: no cover
            stream.point(sign1, phi_mid)  # pragma: no cover
            stream.point(lambda1, phi_mid)  # pragma: no cover
            phi0 = phi_mid  # pragma: no cover
            clean = 0  # pragma: no cover
        elif sign0 != sign1 and delta >= pi:
            l0, l1 = lambda0, lambda1
            if _abs(l0 - sign0) < epsilon:
                l0 -= sign0 * epsilon
            if _abs(l1 - sign1) < epsilon:
                l1 -= sign1 * epsilon
            phi0 = _clip_antimeridian_intersect(l0, phi0, l1, phi1)
            stream.point(sign0, phi0)
            stream.lineEnd()
            stream.lineStart()
            stream.point(sign1, phi0)
            clean = 0
        stream.point(lambda1, phi1)
        lambda0, phi0, sign0 = lambda1, phi1, sign1

    def line_end() -> None:
        nonlocal lambda0, phi0, sign0
        stream.lineEnd()
        lambda0 = phi0 = sign0 = math.nan

    def clean_fn() -> int:
        return 2 - clean

    return {
        "lineStart": line_start,
        "point": point,
        "lineEnd": line_end,
        "clean": clean_fn,
    }


def _always_visible(_lambda: float, _phi: float) -> bool:
    return True


clip_antimeridian = clip(
    _always_visible,
    clip_antimeridian_line,
    clip_antimeridian_interpolate,
    [-pi, -half_pi],
)
