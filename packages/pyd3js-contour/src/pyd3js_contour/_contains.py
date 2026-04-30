"""Ring containment for hole assignment (mirrors d3-contour contains.js)."""

from __future__ import annotations

__all__ = ["contains"]


def contains(ring: list[list[float]], hole: list[list[float]]) -> int:
    i = -1
    n = len(hole)
    while i + 1 < n:
        i += 1
        c = _ring_contains(ring, hole[i])
        if c:
            return c
    return 0


def _ring_contains(ring: list[list[float]], point: list[float]) -> int:
    x = point[0]
    y = point[1]
    ins = -1
    i = 0
    n = len(ring)
    j = n - 1
    while i < n:
        pi = ring[i]
        xi = pi[0]
        yi = pi[1]
        pj = ring[j]
        xj = pj[0]
        yj = pj[1]
        if _segment_contains(pi, pj, point):
            return 0
        if (yi > y) != (yj > y) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            ins = -ins
        j = i
        i += 1
    return ins


def _segment_contains(a: list[float], b: list[float], c: list[float]) -> bool:
    i = 1 if a[0] == b[0] else 0
    return _collinear(a, b, c) and _within(a[i], c[i], b[i])


def _collinear(a: list[float], b: list[float], c: list[float]) -> bool:
    return (b[0] - a[0]) * (c[1] - a[1]) == (c[0] - a[0]) * (b[1] - a[1])


def _within(p: float, q: float, r: float) -> bool:
    return p <= q <= r or r <= q <= p
