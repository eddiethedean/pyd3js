"""interpolateNumber — port of d3-interpolate `number.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def coerce_unary_plus(x: Any, _depth: int = 0) -> float:
    """Approximate JavaScript unary `+` / `ToNumber` for interpolate dispatch and `number.js`.

    `interpolateNumber` coerces **b** once (`b = +b` in JS) but coerces **a** on every tick
    (`a * (1 - t) + b * t` re-applies `ToNumber` to `a`).
    """
    if _depth > 12:
        return float("nan")
    if x is None:
        return float("nan")
    if isinstance(x, bool):
        return float(int(x))
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x.strip())
        except ValueError:
            return float("nan")

    vo = getattr(x, "valueOf", None)
    if callable(vo):
        try:
            p = vo()
        except Exception:
            p = x
        if p is not x:
            return coerce_unary_plus(p, _depth + 1)

    ts = getattr(x, "toString", None)
    if not callable(ts):
        str_m = getattr(type(x), "__str__", None)
        if str_m is not object.__str__:

            def ts() -> str:
                return str(x)

        else:
            ts = None
    if callable(ts):
        try:
            s = ts()
        except Exception:
            s = None
        if isinstance(s, str):
            try:
                return float(s)
            except ValueError:
                return float("nan")

    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def interpolate_number(a: Any, b: Any) -> Callable[[float], float]:
    b0 = coerce_unary_plus(b)

    def f(t: float) -> float:
        a0 = coerce_unary_plus(a)
        return a0 * (1.0 - t) + b0 * t

    return f


__all__ = ["coerce_unary_plus", "interpolate_number"]
