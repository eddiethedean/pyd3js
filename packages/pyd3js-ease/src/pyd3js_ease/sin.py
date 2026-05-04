from __future__ import annotations

import math
from typing import Any

from pyd3js_ease._coerce import ease_t

_half_pi = math.pi / 2.0


def easeSinIn(t: Any) -> float:
    t = ease_t(t)
    if t == 1.0:
        return 1.0
    return 1.0 - math.cos(t * _half_pi)


def easeSinOut(t: Any) -> float:
    t = ease_t(t)
    return math.sin(t * _half_pi)


def easeSinInOut(t: Any) -> float:
    t = ease_t(t)
    return (1.0 - math.cos(math.pi * t)) / 2.0


easeSin = easeSinInOut

__all__ = [
    "easeSin",
    "easeSinIn",
    "easeSinInOut",
    "easeSinOut",
]
