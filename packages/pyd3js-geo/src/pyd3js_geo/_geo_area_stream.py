"""Spherical polygon area accumulation (d3-geo `area.js`)."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array import Adder

quarter_pi = math.pi / 4
tau = 2 * math.pi
degrees = 180 / math.pi
radians = math.pi / 180


def _noop(*_a: Any, **_k: Any) -> None:
    return None


class GeoAreaStream:
    """Streaming spherical excess area (matches `area.js` state machine)."""

    __slots__ = (
        "area_sum",
        "area_ring_sum",
        "_lambda00",
        "_phi00",
        "_lambda0",
        "_cos_phi0",
        "_sin_phi0",
        "point",
        "lineStart",
        "lineEnd",
    )

    def __init__(self) -> None:
        self.area_sum = Adder()
        self.area_ring_sum = Adder()
        self._lambda00 = self._phi00 = 0.0
        self._lambda0 = self._cos_phi0 = self._sin_phi0 = 0.0
        self.point = _noop
        self.lineStart = _noop
        self.lineEnd = _noop

    def sphere(self) -> None:
        self.area_sum.add(tau)

    def polygonStart(self) -> None:
        self.area_ring_sum = Adder()
        self.lineStart = self._area_ring_start
        self.lineEnd = self._area_ring_end

    def polygonEnd(self) -> None:
        area_ring = float(self.area_ring_sum)
        self.area_sum.add((tau + area_ring) if area_ring < 0 else area_ring)
        self.lineStart = _noop
        self.lineEnd = _noop
        self.point = _noop

    def _area_ring_start(self) -> None:
        self.point = self._area_point_first

    def _area_ring_end(self) -> None:
        self._area_point(self._lambda00, self._phi00)

    def _area_point_first(self, lam: float, phi: float, _z: Any = None) -> None:
        self.point = self._area_point
        self._lambda00, self._phi00 = lam, phi
        lam *= radians
        phi *= radians
        self._lambda0 = lam
        phi = phi / 2 + quarter_pi
        self._cos_phi0 = math.cos(phi)
        self._sin_phi0 = math.sin(phi)

    def _area_point(self, lam: float, phi: float, _z: Any = None) -> None:
        lam *= radians
        phi *= radians
        phi = phi / 2 + quarter_pi
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)
        d_lambda = lam - self._lambda0
        sd_lambda = 1 if d_lambda >= 0 else -1
        ad_lambda = sd_lambda * d_lambda
        k = self._sin_phi0 * sin_phi
        u = self._cos_phi0 * cos_phi + k * math.cos(ad_lambda)
        v = k * sd_lambda * math.sin(ad_lambda)
        self.area_ring_sum.add(math.atan2(v, u))
        self._lambda0 = lam
        self._cos_phi0 = cos_phi
        self._sin_phi0 = sin_phi


def geo_area_from_stream(obj: Any) -> float:
    from pyd3js_geo.stream import geoStream

    s = GeoAreaStream()
    geoStream(obj, s)
    return float(s.area_sum) * 2
