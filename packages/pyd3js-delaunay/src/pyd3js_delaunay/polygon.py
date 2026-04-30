"""Polygon point list matching d3-delaunay `src/polygon.js`."""

from __future__ import annotations


class Polygon:
    __slots__ = ("_pts",)

    def __init__(self) -> None:
        self._pts: list[list[float]] = []

    def move_to(self, x: float, y: float) -> None:
        self._pts.append([float(x), float(y)])

    moveTo = move_to

    def close_path(self) -> None:
        if self._pts:
            self._pts.append(self._pts[0][:])

    closePath = close_path

    def line_to(self, x: float, y: float) -> None:
        self._pts.append([float(x), float(y)])

    lineTo = line_to

    def value(self) -> list[list[float]] | None:
        return self._pts if self._pts else None
