"""Mapbox Delaunator — Python port of `delaunator@5.x` (`index.js`)."""

from __future__ import annotations

from array import array
from collections.abc import Iterable, Sequence
from math import ceil, floor, sqrt
from typing import Any, Callable, Union

from pyrobust_predicates import orient2d

EPSILON = pow(2, -52)
EDGE_STACK = [0] * 512


def pseudo_angle(dx: float, dy: float) -> float:
    denom = abs(dx) + abs(dy)
    if denom == 0:
        return 0.25
    p = dx / denom
    return (3 - p if dy > 0 else 1 + p) / 4


def dist(ax: float, ay: float, bx: float, by: float) -> float:
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy


def in_circle(ax: float, ay: float, bx: float, by: float, cx: float, cy: float, px: float, py: float) -> bool:
    dx = ax - px
    dy = ay - py
    ex = bx - px
    ey = by - py
    fx = cx - px
    fy = cy - py

    ap = dx * dx + dy * dy
    bp = ex * ex + ey * ey
    cp = fx * fx + fy * fy

    return (
        dx * (ey * cp - bp * fy)
        - dy * (ex * cp - bp * fx)
        + ap * (ex * fy - ey * fx)
        < 0
    )


def circumradius(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> float:
    dx = bx - ax
    dy = by - ay
    ex = cx - ax
    ey = cy - ay

    bl = dx * dx + dy * dy
    cl = ex * ex + ey * ey
    denom = dx * ey - dy * ex
    if denom == 0:
        return float("inf")
    d = 0.5 / denom

    x = (ey * bl - dy * cl) * d
    y = (dx * cl - ex * bl) * d

    return x * x + y * y


def circumcenter(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> tuple[float, float]:
    dx = bx - ax
    dy = by - ay
    ex = cx - ax
    ey = cy - ay

    bl = dx * dx + dy * dy
    cl = ex * ex + ey * ey
    denom = dx * ey - dy * ex
    if denom == 0:
        return ax, ay
    d = 0.5 / denom

    x = ax + (ey * bl - dy * cl) * d
    y = ay + (dx * cl - ex * bl) * d

    return x, y


def quicksort(ids: array, dists: array, left: int, right: int) -> None:
    if right - left <= 20:
        for i in range(left + 1, right + 1):
            temp = ids[i]
            temp_dist = dists[temp]
            j = i - 1
            while j >= left and dists[ids[j]] > temp_dist:
                ids[j + 1] = ids[j]
                j -= 1
            ids[j + 1] = temp
    else:
        median = (left + right) >> 1
        i = left + 1
        j = right
        ids[median], ids[i] = ids[i], ids[median]
        if dists[ids[left]] > dists[ids[right]]:
            ids[left], ids[right] = ids[right], ids[left]
        if dists[ids[i]] > dists[ids[right]]:
            ids[i], ids[right] = ids[right], ids[i]
        if dists[ids[left]] > dists[ids[i]]:
            ids[left], ids[i] = ids[i], ids[left]

        temp = ids[i]
        temp_dist = dists[temp]
        while True:
            i += 1
            while dists[ids[i]] < temp_dist:
                i += 1
            j -= 1
            while dists[ids[j]] > temp_dist:
                j -= 1
            if j < i:
                break
            ids[i], ids[j] = ids[j], ids[i]
        ids[left + 1] = ids[j]
        ids[j] = temp

        if right - i + 1 >= j - left:
            quicksort(ids, dists, i, right)
            quicksort(ids, dists, left, j - 1)
        else:
            quicksort(ids, dists, left, j - 1)
            quicksort(ids, dists, i, right)


def default_get_x(p: Any, _i: int = 0, _points: Any = None) -> float:
    return float(p[0])


def default_get_y(p: Any, _i: int = 0, _points: Any = None) -> float:
    return float(p[1])


def flat_array(
    points: Sequence[Any],
    fx: Callable[[Any, int, Sequence[Any]], float],
    fy: Callable[[Any, int, Sequence[Any]], float],
    that: Any,
) -> array:
    n = len(points)
    out = array("d", [0.0]) * (n * 2)
    for i in range(n):
        p = points[i]
        out[2 * i] = float(fx(p, i, points))
        out[2 * i + 1] = float(fy(p, i, points))
    return out


def flat_iterable(
    points: Iterable[Any],
    fx: Callable[[Any, int, Any], float],
    fy: Callable[[Any, int, Any], float],
    that: Any,
) -> array:
    plist = list(points)
    coords_list: list[float] = []
    i = 0
    for p in plist:
        coords_list.append(float(fx(p, i, plist)))
        coords_list.append(float(fy(p, i, plist)))
        i += 1
    return array("d", coords_list)


class Delaunator:
    """Triangulation graph matching npm `delaunator` (half-edges, hull, triangles)."""

    coords: array
    triangles: array
    halfedges: array
    hull: array

    def __init__(self, coords: Union[array, Sequence[float]]) -> None:
        if isinstance(coords, array):
            self.coords = coords
        else:
            # Mirror JS: `new Delaunator({ length: -1 })` uses array-like coords with
            # negative `.length`, which becomes `new Uint32Array(-1)` and throws.
            jslen = getattr(coords, "length", None)
            if isinstance(jslen, int) and jslen < 0:
                raise ValueError("Invalid typed array length")
            self.coords = array("d", list(coords))

        n = len(self.coords) >> 1
        if n > 0 and not isinstance(self.coords[0], (int, float)):
            raise ValueError("Expected coords to contain numbers.")

        max_triangles = max(2 * n - 5, 0)
        self._triangles = array("I", [0]) * (max_triangles * 3)
        self._halfedges = array("i", [-1]) * (max_triangles * 3)

        self._hash_size = ceil(sqrt(n)) if n else 0
        self._hull_prev = array("I", [0]) * n
        self._hull_next = array("I", [0]) * n
        self._hull_tri = array("I", [0]) * n
        self._hull_hash = array("i", [-1]) * self._hash_size if self._hash_size else array("i")

        self._ids = array("I", [0]) * n
        self._dists = array("d", [0.0]) * n

        self.triangles_len = 0
        self._hull_start = 0
        self._cx = 0.0
        self._cy = 0.0

        self.update()

    @property
    def trianglesLen(self) -> int:
        """JS-compatible name for `triangles_len` (upstream `d.trianglesLen`)."""
        return self.triangles_len

    @trianglesLen.setter
    def trianglesLen(self, value: int) -> None:
        self.triangles_len = value

    def _hash_key(self, x: float, y: float) -> int:
        return int(floor(pseudo_angle(x - self._cx, y - self._cy) * self._hash_size)) % self._hash_size

    def _link(self, a: int, b: int) -> None:
        self._halfedges[a] = b
        if b != -1:
            self._halfedges[b] = a

    def _add_triangle(self, i0: int, i1: int, i2: int, a: int, b: int, c: int) -> int:
        t = self.triangles_len

        self._triangles[t] = i0
        self._triangles[t + 1] = i1
        self._triangles[t + 2] = i2

        self._link(t, a)
        self._link(t + 1, b)
        self._link(t + 2, c)

        self.triangles_len += 3

        return t

    def _legalize(self, a: int) -> int:
        triangles = self._triangles
        halfedges = self._halfedges
        coords = self.coords

        stack_i = 0
        ar = 0

        while True:
            b = halfedges[a]

            a0 = a - a % 3
            ar = a0 + (a + 2) % 3

            if b == -1:
                if stack_i == 0:
                    break
                stack_i -= 1
                a = EDGE_STACK[stack_i]
                continue

            b0 = b - b % 3
            al = a0 + (a + 1) % 3
            bl = b0 + (b + 2) % 3

            p0 = triangles[ar]
            pr = triangles[a]
            pl = triangles[al]
            p1 = triangles[bl]

            illegal = in_circle(
                coords[2 * p0],
                coords[2 * p0 + 1],
                coords[2 * pr],
                coords[2 * pr + 1],
                coords[2 * pl],
                coords[2 * pl + 1],
                coords[2 * p1],
                coords[2 * p1 + 1],
            )

            if illegal:
                triangles[a] = p1
                triangles[b] = p0

                hbl = halfedges[bl]

                if hbl == -1:
                    e = self._hull_start
                    while True:
                        if self._hull_tri[e] == bl:
                            self._hull_tri[e] = a
                            break
                        e = self._hull_prev[e]
                        if e == self._hull_start:
                            break  # pragma: no cover — defensive; hull should always reference bl
                self._link(a, hbl)
                self._link(b, halfedges[ar])
                self._link(ar, bl)

                br = b0 + (b + 1) % 3

                if stack_i < len(EDGE_STACK):
                    EDGE_STACK[stack_i] = br
                    stack_i += 1
            else:
                if stack_i == 0:
                    break
                stack_i -= 1
                a = EDGE_STACK[stack_i]

        return ar

    def update(self) -> Delaunator:
        coords = self.coords
        hull_prev = self._hull_prev
        hull_next = self._hull_next
        hull_tri = self._hull_tri
        hull_hash = self._hull_hash
        n = len(coords) >> 1

        if n == 0:
            self.triangles_len = 0
            self.hull = array("I")
            self.triangles = array("I")
            self.halfedges = array("i")
            return self

        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")

        for i in range(n):
            x = coords[2 * i]
            y = coords[2 * i + 1]
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
            self._ids[i] = i

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2

        i0 = 0
        min_dist = float("inf")
        for i in range(n):
            d = dist(cx, cy, coords[2 * i], coords[2 * i + 1])
            if d < min_dist:
                i0 = i
                min_dist = d
        i0x = coords[2 * i0]
        i0y = coords[2 * i0 + 1]

        i1 = i0
        min_dist = float("inf")
        for i in range(n):
            if i == i0:
                continue
            d = dist(i0x, i0y, coords[2 * i], coords[2 * i + 1])
            if d < min_dist and d > 0:
                i1 = i
                min_dist = d
        i1x = coords[2 * i1]
        i1y = coords[2 * i1 + 1]

        i2 = i0
        min_radius = float("inf")
        for i in range(n):
            if i == i0 or i == i1:
                continue
            r = circumradius(i0x, i0y, i1x, i1y, coords[2 * i], coords[2 * i + 1])
            if r < min_radius:
                i2 = i
                min_radius = r
        i2x = coords[2 * i2]
        i2y = coords[2 * i2 + 1]

        if min_radius == float("inf"):
            for i in range(n):
                self._dists[i] = (coords[2 * i] - coords[0]) or (coords[2 * i + 1] - coords[1])
            quicksort(self._ids, self._dists, 0, n - 1)
            hull = array("I", [0]) * n
            j = 0
            d0 = float("-inf")
            for i in range(n):
                idx = self._ids[i]
                d = self._dists[idx]
                if d > d0:
                    hull[j] = idx
                    j += 1
                    d0 = d
            self.hull = hull[:j]
            self.triangles_len = 0
            self.triangles = array("I")
            self.halfedges = array("i")
            return self

        if orient2d(i0x, i0y, i1x, i1y, i2x, i2y) < 0:
            i1, i2 = i2, i1
            i1x, i2x = i2x, i1x
            i1y, i2y = i2y, i1y

        center = circumcenter(i0x, i0y, i1x, i1y, i2x, i2y)
        self._cx = center[0]
        self._cy = center[1]

        for i in range(n):
            self._dists[i] = dist(coords[2 * i], coords[2 * i + 1], center[0], center[1])

        quicksort(self._ids, self._dists, 0, n - 1)

        self._hull_start = i0
        hull_size = 3

        hull_next[i0] = hull_prev[i2] = i1
        hull_next[i1] = hull_prev[i0] = i2
        hull_next[i2] = hull_prev[i1] = i0

        hull_tri[i0] = 0
        hull_tri[i1] = 1
        hull_tri[i2] = 2

        for hi in range(self._hash_size):
            hull_hash[hi] = -1
        hull_hash[self._hash_key(i0x, i0y)] = i0
        hull_hash[self._hash_key(i1x, i1y)] = i1
        hull_hash[self._hash_key(i2x, i2y)] = i2

        self.triangles_len = 0
        self._add_triangle(i0, i1, i2, -1, -1, -1)

        xp = 0.0
        yp = 0.0
        for k in range(n):
            i = self._ids[k]
            x = coords[2 * i]
            y = coords[2 * i + 1]

            if k > 0 and abs(x - xp) <= EPSILON and abs(y - yp) <= EPSILON:
                continue
            xp = x
            yp = y

            if i == i0 or i == i1 or i == i2:
                continue

            start = 0
            key = self._hash_key(x, y)
            for j in range(self._hash_size):
                start = hull_hash[(key + j) % self._hash_size]
                if start != -1 and start != hull_next[start]:
                    break

            start = hull_prev[start]
            e = start
            while True:
                q = hull_next[e]
                if (
                    orient2d(
                        x,
                        y,
                        coords[2 * e],
                        coords[2 * e + 1],
                        coords[2 * q],
                        coords[2 * q + 1],
                    )
                    < 0
                ):
                    break
                e = q
                if e == start:
                    e = -1
                    break
            if e == -1:
                continue

            t = self._add_triangle(e, i, hull_next[e], -1, -1, hull_tri[e])

            hull_tri[i] = self._legalize(t + 2)
            hull_tri[e] = t
            hull_size += 1

            nxt = hull_next[e]
            while True:
                q = hull_next[nxt]
                if (
                    orient2d(
                        x,
                        y,
                        coords[2 * nxt],
                        coords[2 * nxt + 1],
                        coords[2 * q],
                        coords[2 * q + 1],
                    )
                    >= 0
                ):
                    break
                t = self._add_triangle(nxt, i, q, hull_tri[i], -1, hull_tri[nxt])
                hull_tri[i] = self._legalize(t + 2)
                hull_next[nxt] = nxt
                hull_size -= 1
                nxt = q

            if e == start:
                while True:
                    q = hull_prev[e]
                    if (
                        orient2d(
                            x,
                            y,
                            coords[2 * q],
                            coords[2 * q + 1],
                            coords[2 * e],
                            coords[2 * e + 1],
                        )
                        >= 0
                    ):
                        break
                    t = self._add_triangle(q, i, e, -1, hull_tri[e], hull_tri[q])
                    self._legalize(t + 2)
                    hull_tri[q] = t
                    hull_next[e] = e
                    hull_size -= 1
                    e = q

            self._hull_start = hull_prev[i] = e
            hull_next[e] = hull_prev[nxt] = i
            hull_next[i] = nxt

            hull_hash[self._hash_key(x, y)] = i
            hull_hash[self._hash_key(coords[2 * e], coords[2 * e + 1])] = e

        self.hull = array("I", [0]) * hull_size
        e = self._hull_start
        for i in range(hull_size):
            self.hull[i] = e
            e = hull_next[e]

        self.triangles = self._triangles[: self.triangles_len]
        self.halfedges = self._halfedges[: self.triangles_len]
        return self

    @classmethod
    def from_points(
        cls,
        points: Union[Sequence[Any], Iterable[Any]],
        fx: Callable[[Any, int, Any], float] | None = None,
        fy: Callable[[Any, int, Any], float] | None = None,
        that: Any = None,
    ) -> Delaunator:
        if fx is None:
            fx = default_get_x
        if fy is None:
            fy = default_get_y
        if hasattr(points, "__len__") and not isinstance(points, (str, bytes)):
            seq = points  # type: ignore[arg-type]
            return cls(flat_array(seq, fx, fy, that))
        return cls(flat_iterable(points, fx, fy, that))
