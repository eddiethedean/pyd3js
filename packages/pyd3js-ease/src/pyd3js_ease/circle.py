from __future__ import annotations

import math
from typing import Any

from pyd3js_ease._coerce import ease_t


def easeCircleIn(t: Any) -> float:
    t = ease_t(t)
    return 1.0 - math.sqrt(1.0 - t * t)


def easeCircleOut(t: Any) -> float:
    t = ease_t(t)
    t -= 1.0
    return math.sqrt(1.0 - t * t)


def easeCircleInOut(t: Any) -> float:
    t = ease_t(t)
    t *= 2.0
    if t <= 1.0:
        return (1.0 - math.sqrt(1.0 - t * t)) / 2.0
    t -= 2.0
    return (math.sqrt(1.0 - t * t) + 1.0) / 2.0


easeCircle = easeCircleInOut

__all__ = [
    "easeCircle",
    "easeCircleIn",
    "easeCircleInOut",
    "easeCircleOut",
]
