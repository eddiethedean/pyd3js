"""`Delaunay` class — port of d3-delaunay `src/delaunay.js`."""

from __future__ import annotations

from array import array
from collections.abc import Iterable, Sequence
from typing import Any, Callable, Iterator, Union
from typing import cast

from pyd3js_delaunay._delaunator import (
    Delaunator,
    default_get_x,
    default_get_y,
    flat_array,
    flat_iterable,
)
from pyd3js_delaunay.path import Path
from pyd3js_delaunay.polygon import Polygon

_TAU = 2 * 3.141592653589793


def _collinear(d: Delaunator) -> bool:
    triangles = d.triangles
    coords = d.coords
    for i in range(0, len(triangles), 3):
        a = 2 * triangles[i]
        b = 2 * triangles[i + 1]
        c = 2 * triangles[i + 2]
        cross = (coords[c] - coords[a]) * (coords[b + 1] - coords[a + 1]) - (
            coords[b] - coords[a]
        ) * (coords[c + 1] - coords[a + 1])
        if cross > 1e-10:
            return False
    return True


def _jitter(x: float, y: float, r: float) -> tuple[float, float]:
    import math

    return x + math.sin(x + y) * r, y + math.cos(x - y) * r


class Delaunay:
    def __init__(self, points: Union[array, Sequence[float]]) -> None:
        self._delaunator = Delaunator(points)
        n = len(self._delaunator.coords) >> 1
        self.inedges = array("i", [-1]) * n
        self._hull_index = array("i", [-1]) * n
        self.points = self._delaunator.coords
        self.collinear: array | None = None
        self._init()

    @classmethod
    def from_points(
        cls,
        points: Union[Sequence[Any], Iterable[Any]],
        fx: Callable[[Any, int, Any], float] | None = None,
        fy: Callable[[Any, int, Any], float] | None = None,
        that: Any = None,
    ) -> Delaunay:
        if fx is None:
            fx = default_get_x
        if fy is None:
            fy = default_get_y
        if hasattr(points, "__len__") and not isinstance(points, (str, bytes)):
            coords = flat_array(cast(Sequence[Any], points), fx, fy, that)
        else:
            coords = flat_iterable(points, fx, fy, that)
        return cls(coords)

    def update(self) -> Delaunay:
        self._delaunator.update()
        self._init()
        return self

    def _init(self) -> None:
        d = self._delaunator
        points = self.points

        if len(d.hull) > 2 and _collinear(d):
            n = len(points) >> 1
            idx = list(range(n))
            idx.sort(key=lambda i: (points[2 * i], points[2 * i + 1]))
            self.collinear = array("i", idx)
            e = self.collinear[0]
            f = self.collinear[len(self.collinear) - 1]
            bounds = (
                points[2 * e],
                points[2 * e + 1],
                points[2 * f],
                points[2 * f + 1],
            )
            import math

            r = 1e-8 * math.hypot(bounds[3] - bounds[1], bounds[2] - bounds[0])
            for i in range(n):
                px, py = _jitter(points[2 * i], points[2 * i + 1], r)
                points[2 * i] = px
                points[2 * i + 1] = py
            self._delaunator = Delaunator(points)
        else:
            self.collinear = None

        halfedges = self.halfedges = self._delaunator.halfedges
        hull = self.hull = self._delaunator.hull
        triangles = self.triangles = self._delaunator.triangles
        inedges = self.inedges
        for hi in range(len(inedges)):
            inedges[hi] = -1
        hull_index = self._hull_index
        for hi in range(len(hull_index)):
            hull_index[hi] = -1

        for e in range(len(halfedges)):
            p = triangles[e - 2 if e % 3 == 2 else e + 1]
            if halfedges[e] == -1 or inedges[p] == -1:
                inedges[p] = e
        for i in range(len(hull)):
            hull_index[hull[i]] = i

        if 0 < len(hull) <= 2:
            self.triangles = array("i", [-1, -1, -1])
            self.halfedges = array("i", [-1, -1, -1])
            self.triangles[0] = hull[0]
            inedges[hull[0]] = 1
            if len(hull) == 2:
                inedges[hull[1]] = 0
                self.triangles[1] = hull[1]
                self.triangles[2] = hull[1]

    def voronoi(self, bounds: Sequence[float] | None = None) -> Any:
        from pyd3js_delaunay.voronoi import Voronoi

        if bounds is None:
            bounds = (0, 0, 960, 500)
        return Voronoi(self, bounds)

    def neighbors(self, i: int) -> Iterator[int]:
        inedges = self.inedges
        hull = self.hull
        hull_index = self._hull_index
        halfedges = self.halfedges
        triangles = self.triangles
        col = self.collinear

        if col is not None:
            try:
                idx = list(col).index(i)
            except ValueError:
                return
            if idx > 0:
                yield col[idx - 1]
            if idx < len(col) - 1:
                yield col[idx + 1]
            return

        e0 = inedges[i]
        if e0 == -1:
            return
        e = e0
        guard = 0
        while True:
            guard += 1
            if guard > len(halfedges) + 8:
                return
            p0 = triangles[e]
            yield p0
            e = e - 2 if e % 3 == 2 else e + 1
            if triangles[e] != i:
                return
            e = halfedges[e]
            if e == -1:
                p = hull[(hull_index[i] + 1) % len(hull)]
                if p != p0:
                    yield p
                return
            if e == e0:
                break

    def find(self, x: float, y: float, i: int = 0) -> int:
        x = float(x)
        y = float(y)
        if x != x or y != y:
            return -1
        i0 = i
        c = self._step(i, x, y)
        while c >= 0 and c != i and c != i0:
            i = c
            c = self._step(i, x, y)
        return c

    def _step(self, i: int, x: float, y: float) -> int:
        inedges = self.inedges
        hull = self.hull
        hull_index = self._hull_index
        halfedges = self.halfedges
        triangles = self.triangles
        points = self.points

        if inedges[i] == -1 or not len(points):
            return (i + 1) % (len(points) >> 1)

        c = i
        dc = (x - points[i * 2]) ** 2 + (y - points[i * 2 + 1]) ** 2
        e0 = inedges[i]
        e = e0
        while True:
            t = triangles[e]
            dt = (x - points[t * 2]) ** 2 + (y - points[t * 2 + 1]) ** 2
            if dt < dc:
                dc = dt
                c = t
            e = e - 2 if e % 3 == 2 else e + 1
            if triangles[e] != i:
                break
            e = halfedges[e]
            if e == -1:
                e = hull[(hull_index[i] + 1) % len(hull)]
                if e != t:
                    if (x - points[e * 2]) ** 2 + (y - points[e * 2 + 1]) ** 2 < dc:
                        return e
                break
            if e == e0:
                break
        return c

    def render(self, context: Any | None = None) -> str | None:
        buffer = None
        if context is None:
            buffer = context = Path()
        points = self.points
        halfedges = self.halfedges
        triangles = self.triangles
        for i in range(len(halfedges)):
            j = halfedges[i]
            if j < i:
                continue
            ti = triangles[i] * 2
            tj = triangles[j] * 2
            context.moveTo(points[ti], points[ti + 1])
            context.lineTo(points[tj], points[tj + 1])
        self.render_hull(context)
        return buffer.value() if buffer is not None else None

    def render_points(self, context: Any | None = None, r: Any = None) -> str | None:
        if r is None and (context is None or not hasattr(context, "moveTo")):
            r = context
            context = None
        if r is None:
            r = 2
        else:
            r = float(r)
        buffer = None
        if context is None:
            buffer = context = Path()
        points = self.points
        for i in range(0, len(points), 2):
            x = points[i]
            y = points[i + 1]
            context.moveTo(x + r, y)
            context.arc(x, y, r, 0, _TAU)
        return buffer.value() if buffer is not None else None

    def render_hull(self, context: Any | None = None) -> str | None:
        buffer = None
        if context is None:
            buffer = context = Path()
        hull = self.hull
        points = self.points
        h = hull[0] * 2
        n = len(hull)
        context.moveTo(points[h], points[h + 1])
        for ii in range(1, n):
            hh = 2 * hull[ii]
            context.lineTo(points[hh], points[hh + 1])
        context.closePath()
        return buffer.value() if buffer is not None else None

    def hull_polygon(self) -> list[list[float]] | None:
        polygon = Polygon()
        self.render_hull(polygon)
        return polygon.value()

    def render_triangle(self, i: int, context: Any | None = None) -> str | None:
        buffer = None
        if context is None:
            buffer = context = Path()
        points = self.points
        triangles = self.triangles
        i *= 3
        t0 = triangles[i] * 2
        t1 = triangles[i + 1] * 2
        t2 = triangles[i + 2] * 2
        context.moveTo(points[t0], points[t0 + 1])
        context.lineTo(points[t1], points[t1 + 1])
        context.lineTo(points[t2], points[t2 + 1])
        context.closePath()
        return buffer.value() if buffer is not None else None

    def triangle_polygons(self) -> Iterator[list[list[float]] | None]:
        n = len(self.triangles) // 3
        for i in range(n):
            yield self.triangle_polygon(i)

    def triangle_polygon(self, i: int) -> list[list[float]] | None:
        polygon = Polygon()
        self.render_triangle(i, polygon)
        return polygon.value()


__all__ = ["Delaunay"]
