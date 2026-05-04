from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t


class PolyIn:
    __slots__ = ("_e",)

    def __init__(self, e: float | str) -> None:
        self._e = float(ease_t(e))

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        return pow(t, self._e)

    def exponent(self, e: Any) -> PolyIn:
        return PolyIn(ease_t(e))


class PolyOut:
    __slots__ = ("_e",)

    def __init__(self, e: float | str) -> None:
        self._e = float(ease_t(e))

    def __call__(self, t: Any, *_args: Any) -> float:
        """Upstream `easePolyOut` ignores extra arguments (e.g. `(t, null)`)."""
        t = ease_t(t)
        return 1.0 - pow(1.0 - t, self._e)

    def exponent(self, e: Any) -> PolyOut:
        return PolyOut(ease_t(e))


class PolyInOut:
    __slots__ = ("_e",)

    def __init__(self, e: float | str) -> None:
        self._e = float(ease_t(e))

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        t *= 2.0
        if t <= 1.0:
            return pow(t, self._e) / 2.0
        return (2.0 - pow(2.0 - t, self._e)) / 2.0

    def exponent(self, e: Any) -> PolyInOut:
        return PolyInOut(ease_t(e))


easePolyIn = PolyIn(3)
easePolyOut = PolyOut(3)
easePolyInOut = PolyInOut(3)
easePoly = easePolyInOut

__all__ = [
    "PolyIn",
    "PolyInOut",
    "PolyOut",
    "easePoly",
    "easePolyIn",
    "easePolyInOut",
    "easePolyOut",
]
