from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t

_b1 = 4.0 / 11.0
_b2 = 6.0 / 11.0
_b3 = 8.0 / 11.0
_b4 = 3.0 / 4.0
_b5 = 9.0 / 11.0
_b6 = 10.0 / 11.0
_b7 = 15.0 / 16.0
_b8 = 21.0 / 22.0
_b9 = 63.0 / 64.0
_b0 = 1.0 / _b1 / _b1


def _bounce_out_raw(t: float) -> float:
    if t < _b1:
        return _b0 * t * t
    if t < _b3:
        t -= _b2
        return _b0 * t * t + _b4
    if t < _b6:
        t -= _b5
        return _b0 * t * t + _b7
    t -= _b8
    return _b0 * t * t + _b9


def easeBounceOut(t: Any) -> float:
    t = ease_t(t)
    return _bounce_out_raw(t)


def easeBounceIn(t: Any) -> float:
    t = ease_t(t)
    return 1.0 - _bounce_out_raw(1.0 - t)


def easeBounceInOut(t: Any) -> float:
    t = ease_t(t)
    t *= 2.0
    if t <= 1.0:
        return (1.0 - _bounce_out_raw(1.0 - t)) / 2.0
    return (_bounce_out_raw(t - 1.0) + 1.0) / 2.0


easeBounce = easeBounceOut

__all__ = [
    "easeBounce",
    "easeBounceIn",
    "easeBounceInOut",
    "easeBounceOut",
]
