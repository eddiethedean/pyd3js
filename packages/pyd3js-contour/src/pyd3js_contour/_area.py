"""Ring signed area (mirrors d3-contour area.js)."""

from __future__ import annotations

__all__ = ["area"]


def area(ring: list[list[float]]) -> float:
    i = 0
    n = len(ring)
    a = ring[n - 1][1] * ring[0][0] - ring[n - 1][0] * ring[0][1]
    while i + 1 < n:
        i += 1
        a += ring[i - 1][1] * ring[i][0] - ring[i - 1][0] * ring[i][1]
    return a
