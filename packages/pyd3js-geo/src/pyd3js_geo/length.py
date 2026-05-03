"""Geodesic length (d3-geo `length.js`)."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array import Adder

from pyd3js_geo.math import radians
from pyd3js_geo.noop import noop
from pyd3js_geo.stream import geoStream


class _LengthStream:
    def __init__(self):
        self.sum = Adder()
        self.point = noop
        self.lineEnd = noop

    def sphere(self):
        pass

    def polygonStart(self):
        pass

    def polygonEnd(self):
        pass

    def lineStart(self):
        self.point = self._first
        self.lineEnd = self._end

    def _end(self):
        self.point = noop
        self.lineEnd = noop

    def _first(self, lambda_: float, phi: float, z: Any = None):
        self.lambda0 = lambda_ * radians
        phi *= radians
        self.sinPhi0, self.cosPhi0 = math.sin(phi), math.cos(phi)
        self.point = self._point

    def _point(self, lambda_: float, phi: float, z: Any = None):
        lambda_, phi = lambda_ * radians, phi * radians
        sp, cp = math.sin(phi), math.cos(phi)
        delta = abs(lambda_ - self.lambda0)
        cd, sd = math.cos(delta), math.sin(delta)
        x = cp * sd
        y = self.cosPhi0 * sp - self.sinPhi0 * cp * cd
        zz = self.sinPhi0 * sp + self.cosPhi0 * cp * cd
        self.sum.add(math.atan2(math.sqrt(x * x + y * y), zz))
        self.lambda0, self.sinPhi0, self.cosPhi0 = lambda_, sp, cp


def geoLength(obj: Any) -> float:
    s = _LengthStream()
    geoStream(obj, s)
    return float(s.sum)
