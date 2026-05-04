from __future__ import annotations

import math
from typing import Any

from pyd3js_ease._coerce import ease_t
from pyd3js_ease._math import tpmt

_tau = 2.0 * math.pi


class ElasticIn:
    __slots__ = ("_a", "_p", "_s")

    def __init__(self, a: float | str, p_user: float | str) -> None:
        self._a = max(1.0, float(ease_t(a)))
        self._p = float(ease_t(p_user)) / _tau
        self._s = math.asin(1.0 / self._a) * self._p

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        t -= 1.0
        return self._a * tpmt(-t) * math.sin((self._s - t) / self._p)

    def amplitude(self, a: Any) -> ElasticIn:
        p_user = self._p * _tau
        return ElasticIn(ease_t(a), p_user)

    def period(self, p: Any) -> ElasticIn:
        return ElasticIn(self._a, ease_t(p))


class ElasticOut:
    __slots__ = ("_a", "_p", "_s")

    def __init__(self, a: float | str, p_user: float | str) -> None:
        self._a = max(1.0, float(ease_t(a)))
        self._p = float(ease_t(p_user)) / _tau
        self._s = math.asin(1.0 / self._a) * self._p

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        return 1.0 - self._a * tpmt(t) * math.sin((t + self._s) / self._p)

    def amplitude(self, a: Any) -> ElasticOut:
        p_user = self._p * _tau
        return ElasticOut(ease_t(a), p_user)

    def period(self, p: Any) -> ElasticOut:
        return ElasticOut(self._a, ease_t(p))


class ElasticInOut:
    __slots__ = ("_a", "_p", "_s")

    def __init__(self, a: float | str, p_user: float | str) -> None:
        self._a = max(1.0, float(ease_t(a)))
        self._p = float(ease_t(p_user)) / _tau
        self._s = math.asin(1.0 / self._a) * self._p

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        t = t * 2.0 - 1.0
        if t < 0.0:
            return self._a * tpmt(-t) * math.sin((self._s - t) / self._p) / 2.0
        return (2.0 - self._a * tpmt(t) * math.sin((self._s + t) / self._p)) / 2.0

    def amplitude(self, a: Any) -> ElasticInOut:
        p_user = self._p * _tau
        return ElasticInOut(ease_t(a), p_user)

    def period(self, p: Any) -> ElasticInOut:
        return ElasticInOut(self._a, ease_t(p))


easeElasticIn = ElasticIn(1, 0.3)
easeElasticOut = ElasticOut(1, 0.3)
easeElasticInOut = ElasticInOut(1, 0.3)
easeElastic = easeElasticOut

__all__ = [
    "ElasticIn",
    "ElasticInOut",
    "ElasticOut",
    "easeElastic",
    "easeElasticIn",
    "easeElasticInOut",
    "easeElasticOut",
]
