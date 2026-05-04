from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t
from pyd3js_ease._math import tpmt


def easeExpIn(t: Any) -> float:
    t = ease_t(t)
    return tpmt(1.0 - t)


def easeExpOut(t: Any) -> float:
    t = ease_t(t)
    return 1.0 - tpmt(t)


def easeExpInOut(t: Any) -> float:
    t = ease_t(t)
    t *= 2.0
    if t <= 1.0:
        return tpmt(1.0 - t) / 2.0
    return (2.0 - tpmt(t - 1.0)) / 2.0


easeExp = easeExpInOut

__all__ = [
    "easeExp",
    "easeExpIn",
    "easeExpInOut",
    "easeExpOut",
]
