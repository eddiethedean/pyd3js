"""SVG path string builder matching d3-delaunay `src/path.js`."""

from __future__ import annotations

_EPSILON = 1e-6


def _fmt(n: float) -> str:
    """Format a number like JS `String(+x)` (integers without a decimal part)."""
    n = float(n)
    if n == int(n) and abs(n) < 1e15:
        return str(int(n))
    t = f"{n:.12f}".rstrip("0").rstrip(".")
    return t if t not in ("-0", "") else "0"


class Path:
    """Minimal canvas-like path recorder producing SVG path `d` strings."""

    __slots__ = ("_x0", "_y0", "_x1", "_y1", "_")

    def __init__(self) -> None:
        self._x0 = self._y0 = self._x1 = self._y1 = None  # type: ignore[assignment]
        self._ = ""

    def move_to(self, x: float, y: float) -> None:
        x = float(x)
        y = float(y)
        self._ += f"M{_fmt(x)},{_fmt(y)}"
        self._x0 = self._x1 = x
        self._y0 = self._y1 = y

    moveTo = move_to

    def close_path(self) -> None:
        if self._x1 is not None:
            self._x1 = self._x0
            self._y1 = self._y0
            self._ += "Z"

    closePath = close_path

    def line_to(self, x: float, y: float) -> None:
        x = float(x)
        y = float(y)
        self._ += f"L{_fmt(x)},{_fmt(y)}"
        self._x1 = x
        self._y1 = y

    lineTo = line_to

    def arc(self, x: float, y: float, r: float, *_args: float) -> None:
        x = float(x)
        y = float(y)
        r = float(r)
        x0 = x + r
        y0 = y
        if r < 0:
            raise ValueError("negative radius")
        if self._x1 is None:
            self._ += f"M{_fmt(x0)},{_fmt(y0)}"
        elif abs(self._x1 - x0) > _EPSILON or abs(self._y1 - y0) > _EPSILON:
            self._ += f"L{_fmt(x0)},{_fmt(y0)}"
        if not r:
            return
        self._ += f"A{_fmt(r)},{_fmt(r)},0,1,1,{_fmt(x - r)},{_fmt(y)}A{_fmt(r)},{_fmt(r)},0,1,1,{_fmt(x0)},{_fmt(y0)}"
        self._x1 = x0
        self._y1 = y0

    def rect(self, x: float, y: float, w: float, h: float) -> None:
        x = float(x)
        y = float(y)
        w = float(w)
        h = float(h)
        self._ += f"M{_fmt(x)},{_fmt(y)}h{_fmt(w)}v{_fmt(h)}h{_fmt(-w)}Z"
        self._x0 = self._x1 = x
        self._y0 = self._y1 = y

    def value(self) -> str | None:
        return self._ or None


__all__ = ["Path"]
