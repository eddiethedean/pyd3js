"""Cohen–Sutherland line clip (d3-geo `clip/line.js`)."""

from __future__ import annotations


def clip_line_rect(
    a: list[float],
    b: list[float],
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> bool:
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    t0, t1 = 0.0, 1.0
    dx = bx - ax
    dy = by - ay
    r: float

    r = x0 - ax
    if not dx and r > 0:
        return False
    if dx:
        r /= dx
        if dx < 0:
            if r < t0:
                return False
            if r < t1:
                t1 = r
        elif dx > 0:
            if r > t1:
                return False
            if r > t0:
                t0 = r

    r = x1 - ax
    if not dx and r < 0:
        return False
    if dx:
        r /= dx
        if dx < 0:
            if r > t1:
                return False
            if r > t0:
                t0 = r
        elif dx > 0:
            if r < t0:
                return False
            if r < t1:
                t1 = r

    r = y0 - ay
    if not dy and r > 0:
        return False
    if dy:
        r /= dy
        if dy < 0:
            if r < t0:
                return False  # pragma: no cover
            if r < t1:
                t1 = r
        elif dy > 0:
            if r > t1:
                return False
            if r > t0:
                t0 = r

    r = y1 - ay
    if not dy and r < 0:
        return False
    if dy:
        r /= dy
        if dy < 0:
            if r > t1:
                return False
            if r > t0:
                t0 = r
        elif dy > 0:
            if r < t0:
                return False
            if r < t1:
                t1 = r

    if t0 > 0:
        a[0] = ax + t0 * dx
        a[1] = ay + t0 * dy
    if t1 < 1:
        b[0] = ax + t1 * dx
        b[1] = ay + t1 * dy
    return True
