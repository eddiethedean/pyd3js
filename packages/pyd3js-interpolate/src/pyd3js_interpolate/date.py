"""interpolateDate — port of d3-interpolate `date.js`."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any


def interpolate_date(a: Any, b: Any) -> Callable[[float], datetime]:
    if not isinstance(a, datetime):
        a = datetime.fromtimestamp(float(a) / 1000.0)
    if not isinstance(b, datetime):
        b = datetime.fromtimestamp(float(b) / 1000.0)
    delta = b - a

    def f(t: float) -> datetime:
        return a + delta * t

    return f


__all__ = ["interpolate_date"]
