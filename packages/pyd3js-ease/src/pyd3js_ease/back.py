from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t

_overshoot = 1.70158


class BackIn:
    __slots__ = ("_s",)

    def __init__(self, s: float | str) -> None:
        self._s = float(ease_t(s))

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        return t * t * (self._s * (t - 1.0) + t)

    def overshoot(self, s: Any) -> BackIn:
        return BackIn(ease_t(s))


class BackOut:
    __slots__ = ("_s",)

    def __init__(self, s: float | str) -> None:
        self._s = float(ease_t(s))

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        t -= 1.0
        return t * t * ((t + 1.0) * self._s + t) + 1.0

    def overshoot(self, s: Any) -> BackOut:
        return BackOut(ease_t(s))


class BackInOut:
    __slots__ = ("_s",)

    def __init__(self, s: float | str) -> None:
        self._s = float(ease_t(s))

    def __call__(self, t: Any) -> float:
        t = ease_t(t)
        t *= 2.0
        if t < 1.0:
            return t * t * ((self._s + 1.0) * t - self._s) / 2.0
        t -= 2.0
        return (t * t * ((self._s + 1.0) * t + self._s) + 2.0) / 2.0

    def overshoot(self, s: Any) -> BackInOut:
        return BackInOut(ease_t(s))


easeBackIn = BackIn(_overshoot)
easeBackOut = BackOut(_overshoot)
easeBackInOut = BackInOut(_overshoot)
easeBack = easeBackInOut

__all__ = [
    "BackIn",
    "BackInOut",
    "BackOut",
    "easeBack",
    "easeBackIn",
    "easeBackInOut",
    "easeBackOut",
]
