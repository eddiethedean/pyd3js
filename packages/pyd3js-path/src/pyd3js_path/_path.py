from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

_PI = math.pi
_TAU = 2 * _PI
_EPSILON = 1e-6
_TAU_EPSILON = _TAU - _EPSILON


def _js_number(x: float) -> str:
    # Python's repr(float) is a short, round-trippable representation that is
    # close to JS number-to-string for the values we care about in d3-path.
    if math.isfinite(x) and abs(x - round(x)) < _EPSILON:
        return str(int(round(x)))
    return repr(float(x))


def _append_round(digits: Any):
    try:
        d = math.floor(float(digits))
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"invalid digits: {digits}") from e
    if not (d >= 0):
        raise ValueError(f"invalid digits: {digits}")
    if d > 15:
        return None
    k = 10 ** int(d)

    def _round(x: float) -> float:
        return round(x * k) / k

    return _round


@dataclass
class _State:
    x0: Optional[float] = None
    y0: Optional[float] = None
    x1: Optional[float] = None
    y1: Optional[float] = None
    s: str = ""


class Path:
    def __init__(self, digits: Any = None):
        self._state = _State()
        self._round = None if digits is None else _append_round(digits)

    def _num(self, x: float) -> str:
        if self._round is not None:
            x = self._round(float(x))
        return _js_number(float(x))

    def moveTo(self, x: float, y: float) -> None:
        x = float(x)
        y = float(y)
        st = self._state
        st.x0 = st.x1 = x
        st.y0 = st.y1 = y
        st.s += f"M{self._num(x)},{self._num(y)}"

    def closePath(self) -> None:
        st = self._state
        if st.x1 is not None:
            st.x1 = st.x0
            st.y1 = st.y0
            st.s += "Z"

    def lineTo(self, x: float, y: float) -> None:
        x = float(x)
        y = float(y)
        st = self._state
        st.x1 = x
        st.y1 = y
        st.s += f"L{self._num(x)},{self._num(y)}"

    def quadraticCurveTo(self, x1: float, y1: float, x: float, y: float) -> None:
        x1 = float(x1)
        y1 = float(y1)
        x = float(x)
        y = float(y)
        st = self._state
        st.x1 = x
        st.y1 = y
        st.s += f"Q{self._num(x1)},{self._num(y1)},{self._num(x)},{self._num(y)}"

    def bezierCurveTo(
        self, x1: float, y1: float, x2: float, y2: float, x: float, y: float
    ) -> None:
        x1 = float(x1)
        y1 = float(y1)
        x2 = float(x2)
        y2 = float(y2)
        x = float(x)
        y = float(y)
        st = self._state
        st.x1 = x
        st.y1 = y
        st.s += f"C{self._num(x1)},{self._num(y1)},{self._num(x2)},{self._num(y2)},{self._num(x)},{self._num(y)}"

    def arcTo(self, x1: float, y1: float, x2: float, y2: float, r: float) -> None:
        x1 = float(x1)
        y1 = float(y1)
        x2 = float(x2)
        y2 = float(y2)
        r = float(r)
        if r < 0:
            raise ValueError(f"negative radius: {r}")

        st = self._state
        x0 = st.x1
        y0 = st.y1

        x21 = x2 - x1
        y21 = y2 - y1
        if x0 is None or y0 is None:
            st.s += f"M{self._num(x1)},{self._num(y1)}"
            st.x1 = x1
            st.y1 = y1
            return

        x01 = x0 - x1
        y01 = y0 - y1
        l01_2 = x01 * x01 + y01 * y01

        if not (l01_2 > _EPSILON):
            return

        if not (abs(y01 * x21 - y21 * x01) > _EPSILON) or not r:
            st.s += f"L{self._num(x1)},{self._num(y1)}"
            st.x1 = x1
            st.y1 = y1
            return

        x20 = x2 - x0
        y20 = y2 - y0
        l21_2 = x21 * x21 + y21 * y21
        l20_2 = x20 * x20 + y20 * y20
        l21 = math.sqrt(l21_2)
        l01 = math.sqrt(l01_2)
        tangent_length = r * math.tan(
            (_PI - math.acos((l21_2 + l01_2 - l20_2) / (2 * l21 * l01))) / 2
        )
        t01 = tangent_length / l01
        t21 = tangent_length / l21

        if abs(t01 - 1) > _EPSILON:
            st.s += f"L{self._num(x1 + t01 * x01)},{self._num(y1 + t01 * y01)}"

        sweep = 1 if (y01 * x20 > x01 * y20) else 0
        st.x1 = x1 + t21 * x21
        st.y1 = y1 + t21 * y21
        st.s += f"A{self._num(r)},{self._num(r)},0,0,{sweep},{self._num(st.x1)},{self._num(st.y1)}"

    def arc(
        self, x: float, y: float, r: float, a0: float, a1: float, ccw: Any = False
    ) -> None:
        x = float(x)
        y = float(y)
        r = float(r)
        ccw_bool = bool(ccw)

        if r < 0:
            raise ValueError(f"negative radius: {r}")

        dx = r * math.cos(a0)
        dy = r * math.sin(a0)
        x0 = x + dx
        y0 = y + dy
        cw = 1 ^ int(ccw_bool)
        da = (a0 - a1) if ccw_bool else (a1 - a0)

        st = self._state
        had_point = st.x1 is not None and st.y1 is not None
        if not had_point:
            st.s += f"M{self._num(x0)},{self._num(y0)}"
        elif abs(st.x1 - x0) > _EPSILON or abs(st.y1 - y0) > _EPSILON:
            st.s += f"L{self._num(x0)},{self._num(y0)}"

        if not r:
            return

        if da < 0:
            # JS `%` keeps the sign of the dividend; Python `%` does not.
            da = math.fmod(da, _TAU) + _TAU

        if da > _TAU_EPSILON:
            st.s += (
                f"A{self._num(r)},{self._num(r)},0,1,{cw},{self._num(x - dx)},{self._num(y - dy)}"
                f"A{self._num(r)},{self._num(r)},0,1,{cw},{self._num(x0)},{self._num(y0)}"
            )
            st.x1 = x0
            st.y1 = y0
        elif da > _EPSILON:
            st.x1 = x + r * math.cos(a1)
            st.y1 = y + r * math.sin(a1)
            large = 1 if da >= _PI else 0
            st.s += f"A{self._num(r)},{self._num(r)},0,{large},{cw},{self._num(st.x1)},{self._num(st.y1)}"

    def rect(self, x: float, y: float, w: float, h: float) -> None:
        x = float(x)
        y = float(y)
        w = float(w)
        h = float(h)
        st = self._state
        st.x0 = st.x1 = x
        st.y0 = st.y1 = y
        st.s += f"M{self._num(x)},{self._num(y)}h{self._num(w)}v{self._num(h)}h{self._num(-w)}Z"

    def __str__(self) -> str:
        return self._state.s

    def __repr__(self) -> str:
        return f"Path({self._state.s!r})"


class _PathFactoryMeta(type):
    def __call__(cls) -> Path:  # calling `path()` returns a Path, like d3-path
        return Path()

    def __instancecheck__(cls, instance: object) -> bool:
        # mimic JS `p instanceof path` behavior
        return isinstance(instance, Path)


class path(metaclass=_PathFactoryMeta):
    """Factory/type for d3-path compatibility."""


def pathRound(digits: Any = 3) -> Path:
    if digits is None:
        digits = 0
    return Path(float(digits))
