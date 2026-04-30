"""`Voronoi` class — port of d3-delaunay `src/voronoi.js`."""

from __future__ import annotations

from array import array
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, Any

from pyd3js_delaunay.path import Path
from pyd3js_delaunay.polygon import Polygon

if TYPE_CHECKING:
    from pyd3js_delaunay.delaunay import Delaunay


class CellPolygon(list):
    """Closed Voronoi cell vertices ``[x,y], ...`` with ``index`` (internal yield type)."""

    def __init__(self, vertices: list[list[float]], index: int) -> None:
        super().__init__(vertices)
        self.index = index


class Voronoi:
    def __init__(self, delaunay: Delaunay, bounds: Sequence[float] | None = None) -> None:
        if bounds is None:
            bounds = (0, 0, 960, 500)
        xmin, ymin, xmax, ymax = float(bounds[0]), float(bounds[1]), float(bounds[2]), float(bounds[3])
        xmax, xmin, ymax, ymin = +xmax, +xmin, +ymax, +ymin
        if not (xmax >= xmin) or not (ymax >= ymin):
            raise ValueError("invalid bounds")
        self.delaunay = delaunay
        ncoords = len(delaunay.points)
        self._circumcenters = array("d", [0.0]) * ncoords
        self.vectors = array("d", [0.0]) * (ncoords * 2)
        self.xmax, self.xmin = xmax, xmin
        self.ymax, self.ymin = ymax, ymin
        self.circumcenters: array | None = None
        self._init()

    def update(self) -> Voronoi:
        self.delaunay.update()
        self._init()
        return self

    def _init(self) -> None:
        points = self.delaunay.points
        hull = self.delaunay.hull
        triangles = self.delaunay.triangles
        vectors = self.vectors
        bx = by = None
        nt = len(triangles) // 3
        circumcenters = self.circumcenters = array("d", [0.0]) * (nt * 2)
        j = 0
        for i in range(0, len(triangles), 3):
            t1, t2, t3 = triangles[i] * 2, triangles[i + 1] * 2, triangles[i + 2] * 2
            x1, y1 = points[t1], points[t1 + 1]
            x2, y2 = points[t2], points[t2 + 1]
            x3, y3 = points[t3], points[t3 + 1]
            dx, dy = x2 - x1, y2 - y1
            ex, ey = x3 - x1, y3 - y1
            ab = (dx * ey - dy * ex) * 2
            if abs(ab) < 1e-9:
                if bx is None:
                    bx = by = 0.0
                    for hi in hull:
                        bx += points[hi * 2]
                        by += points[hi * 2 + 1]
                    bx /= len(hull)
                    by /= len(hull)
                sgn = 1.0 if (bx - x1) * ey - (by - y1) * ex >= 0 else -1.0
                a = 1e9 * sgn
                x = (x1 + x3) / 2 - a * ey
                y = (y1 + y3) / 2 + a * ex
            else:
                d = 1 / ab
                bl, cl = dx * dx + dy * dy, ex * ex + ey * ey
                x = x1 + (ey * bl - dy * cl) * d
                y = y1 + (dx * cl - ex * bl) * d
            circumcenters[j], circumcenters[j + 1] = x, y
            j += 2
        for vi in range(len(vectors)):
            vectors[vi] = 0.0
        if len(hull):
            h1 = hull[-1]
            p1 = h1 * 4
            x1, y1 = points[2 * h1], points[2 * h1 + 1]
            for _ in range(len(hull)):
                h0 = h1
                x0, y0 = x1, y1
                h1 = hull[_]
                p0 = p1
                p1 = h1 * 4
                x1, y1 = points[2 * h1], points[2 * h1 + 1]
                vectors[p0 + 2] = vectors[p1] = y0 - y1
                vectors[p0 + 3] = vectors[p1 + 1] = x1 - x0

    def render(self, context: Any | None = None) -> str | None:
        buffer = None if context is not None else Path()
        if context is None:
            context = buffer
        halfedges = self.delaunay.halfedges
        inedges = self.delaunay.inedges
        hull = self.delaunay.hull
        circumcenters = self.circumcenters
        vectors = self.vectors
        if circumcenters is None or len(hull) <= 1:
            return buffer.value() if buffer else None
        for i in range(len(halfedges)):
            j = halfedges[i]
            if j < i:
                continue
            ti, tj = (i // 3) * 2, (j // 3) * 2
            self._render_segment(
                circumcenters[ti],
                circumcenters[ti + 1],
                circumcenters[tj],
                circumcenters[tj + 1],
                context,
            )
        h1 = hull[-1]
        for hi in range(len(hull)):
            h0, h1 = h1, hull[hi]
            t = (inedges[h1] // 3) * 2
            x, y = circumcenters[t], circumcenters[t + 1]
            v = h0 * 4
            p = self._project(x, y, vectors[v + 2], vectors[v + 3])
            if p:
                self._render_segment(x, y, p[0], p[1], context)
        return buffer.value() if buffer else None

    def render_bounds(self, context: Any | None = None) -> str | None:
        buffer = None if context is not None else Path()
        if context is None:
            context = buffer
        context.rect(self.xmin, self.ymin, self.xmax - self.xmin, self.ymax - self.ymin)
        return buffer.value() if buffer else None

    renderBounds = render_bounds

    def render_cell(self, i: int, context: Any | None = None) -> str | None:
        buffer = None if context is not None else Path()
        if context is None:
            context = buffer
        pts = self._clip(i)
        if pts is None or not len(pts):
            return buffer.value() if buffer else None
        context.moveTo(pts[0], pts[1])
        n = len(pts)
        while pts[0] == pts[n - 2] and pts[1] == pts[n - 1] and n > 1:
            n -= 2
        for k in range(2, n, 2):
            if pts[k] != pts[k - 2] or pts[k + 1] != pts[k - 1]:
                context.lineTo(pts[k], pts[k + 1])
        context.closePath()
        return buffer.value() if buffer else None

    renderCell = render_cell

    def cell_polygons(self) -> Iterator[CellPolygon]:
        n = len(self.delaunay.points) // 2
        for i in range(n):
            cell = self.cell_polygon(i)
            if cell:
                yield CellPolygon(cell, i)

    cellPolygons = cell_polygons

    def cell_polygon(self, i: int) -> list[list[float]] | None:
        poly = Polygon()
        self.render_cell(i, poly)
        return poly.value()

    cellPolygon = cell_polygon

    def _render_segment(self, x0: float, y0: float, x1: float, y1: float, context: Any) -> None:
        c0, c1 = self._regioncode(x0, y0), self._regioncode(x1, y1)
        if c0 == 0 and c1 == 0:
            context.moveTo(x0, y0)
            context.lineTo(x1, y1)
            return
        s = self._clip_segment(x0, y0, x1, y1, c0, c1)
        if s:
            context.moveTo(s[0], s[1])
            context.lineTo(s[2], s[3])

    def contains(self, i: int, x: float, y: float) -> bool:
        x, y = float(x), float(y)
        if x != x or y != y:
            return False
        return self.delaunay._step(i, x, y) == i

    def neighbors(self, i: int) -> Iterator[int]:
        ci = self._clip(i)
        if not ci:
            return
        for j in self.delaunay.neighbors(i):
            cj = self._clip(j)
            if not cj:
                continue
            li, lj = len(ci), len(cj)
            found = False
            for ai in range(0, li, 2):
                for aj in range(0, lj, 2):
                    if (
                        ci[ai] == cj[aj]
                        and ci[ai + 1] == cj[aj + 1]
                        and ci[(ai + 2) % li] == cj[(aj + lj - 2) % lj]
                        and ci[(ai + 3) % li] == cj[(aj + lj - 1) % lj]
                    ):
                        yield j
                        found = True
                        break
                if found:
                    break

    def _cell(self, i: int) -> list[float] | None:
        circumcenters = self.circumcenters
        if circumcenters is None:
            return None
        inedges = self.delaunay.inedges
        halfedges = self.delaunay.halfedges
        triangles = self.delaunay.triangles
        e0 = inedges[i]
        if e0 == -1:
            return None
        out: list[float] = []
        e = e0
        while True:
            t = e // 3
            out.extend([circumcenters[t * 2], circumcenters[t * 2 + 1]])
            e = e - 2 if e % 3 == 2 else e + 1
            if triangles[e] != i:
                break
            e = halfedges[e]
            if e == e0 or e == -1:
                break
        return out

    def _clip(self, i: int) -> list[float] | None:
        if i == 0 and len(self.delaunay.hull) == 1:
            return [
                self.xmax,
                self.ymin,
                self.xmax,
                self.ymax,
                self.xmin,
                self.ymax,
                self.xmin,
                self.ymin,
            ]
        pts = self._cell(i)
        if pts is None:
            return None
        v = i * 4
        vv = self.vectors
        if vv[v] or vv[v + 1]:
            return self._simplify(
                self._clip_infinite(i, pts, vv[v], vv[v + 1], vv[v + 2], vv[v + 3])
            )
        return self._simplify(self._clip_finite(i, pts))

    def _clip_finite(self, i: int, points: list[float]) -> list[float] | None:
        n = len(points)
        p: list[float] | None = None
        x1, y1 = points[n - 2], points[n - 1]
        c1 = self._regioncode(x1, y1)
        e0 = e1 = 0
        for jj in range(0, n, 2):
            x0, y0 = x1, y1
            x1, y1 = points[jj], points[jj + 1]
            c0, c1 = c1, self._regioncode(x1, y1)
            if c0 == 0 and c1 == 0:
                e0, e1 = e1, 0
                if p:
                    p.extend([x1, y1])
                else:
                    p = [x1, y1]
            else:
                if c0 == 0:
                    s = self._clip_segment(x0, y0, x1, y1, c0, c1)
                    if s is None:
                        continue
                    sx0, sy0, sx1, sy1 = s
                else:
                    s = self._clip_segment(x1, y1, x0, y0, c1, c0)
                    if s is None:
                        continue
                    sx1, sy1, sx0, sy0 = s
                    e0, e1 = e1, self._edgecode(sx0, sy0)
                    if e0 and e1:
                        self._edge(i, e0, e1, p, len(p) if p else 0)
                    if p:
                        p.extend([sx0, sy0])
                    else:
                        p = [sx0, sy0]
                e0, e1 = e1, self._edgecode(sx1, sy1)
                if e0 and e1:
                    self._edge(i, e0, e1, p, len(p) if p else 0)
                if p:
                    p.extend([sx1, sy1])
                else:
                    p = [sx1, sy1]
        if p:
            e0, e1 = e1, self._edgecode(p[0], p[1])
            if e0 and e1:
                self._edge(i, e0, e1, p, len(p))
        elif self.contains(i, (self.xmin + self.xmax) / 2, (self.ymin + self.ymax) / 2):
            return [
                self.xmax,
                self.ymin,
                self.xmax,
                self.ymax,
                self.xmin,
                self.ymax,
                self.xmin,
                self.ymin,
            ]
        return p

    def _clip_segment(
        self, x0: float, y0: float, x1: float, y1: float, c0: int, c1: int
    ) -> list[float] | None:
        flip = c0 < c1
        if flip:
            x0, y0, x1, y1, c0, c1 = x1, y1, x0, y0, c1, c0
        _eps = 1e-12
        for _ in range(64):
            if c0 == 0 and c1 == 0:
                return [x1, y1, x0, y0] if flip else [x0, y0, x1, y1]
            if c0 & c1:
                return None
            c = c0 or c1
            if c & 0b1000:
                dy = y1 - y0
                if abs(dy) < _eps:
                    return None
                x = x0 + (x1 - x0) * (self.ymax - y0) / dy
                y = self.ymax
            elif c & 0b0100:
                dy = y1 - y0
                if abs(dy) < _eps:
                    return None
                x = x0 + (x1 - x0) * (self.ymin - y0) / dy
                y = self.ymin
            elif c & 0b0010:
                dx = x1 - x0
                if abs(dx) < _eps:
                    return None
                y = y0 + (y1 - y0) * (self.xmax - x0) / dx
                x = self.xmax
            else:
                dx = x1 - x0
                if abs(dx) < _eps:
                    return None
                y = y0 + (y1 - y0) * (self.xmin - x0) / dx
                x = self.xmin
            if c0:
                x0, y0 = x, y
                c0 = self._regioncode(x0, y0)
            else:
                x1, y1 = x, y
                c1 = self._regioncode(x1, y1)
        return None

    def _clip_infinite(
        self, i: int, points: list[float], vx0: float, vy0: float, vxn: float, vyn: float
    ) -> list[float] | None:
        p = list(points)
        pr = self._project(p[0], p[1], vx0, vy0)
        if pr:
            p.insert(0, pr[1])
            p.insert(0, pr[0])
        pr = self._project(p[-2], p[-1], vxn, vyn)
        if pr:
            p.extend(pr)
        clipped = self._clip_finite(i, p)
        if clipped:
            j = 0
            n = len(clipped)
            c1 = self._edgecode(clipped[n - 2], clipped[n - 1])
            guard = 0
            while j < n:
                guard += 1
                if guard > max(200, n * 8):
                    break
                c0, c1 = c1, self._edgecode(clipped[j], clipped[j + 1])
                if c0 and c1:
                    j_new = self._edge(i, c0, c1, clipped, j)
                    if j_new == j and n == len(clipped):
                        j += 2
                    else:
                        j = j_new
                    n = len(clipped)
                else:
                    j += 2
            return clipped
        if self.contains(i, (self.xmin + self.xmax) / 2, (self.ymin + self.ymax) / 2):
            return [
                self.xmin,
                self.ymin,
                self.xmax,
                self.ymin,
                self.xmax,
                self.ymax,
                self.xmin,
                self.ymax,
            ]
        return clipped

    def _edge(self, i: int, e0: int, e1: int, p: list[float] | None, j: int) -> int:
        if p is None:
            return j
        guard = 0
        while e0 != e1:
            guard += 1
            if guard > 48:
                break
            x = y = None
            if e0 == 0b0101:
                e0 = 0b0100
                continue
            if e0 == 0b0100:
                e0 = 0b0110
                x, y = self.xmax, self.ymin
            elif e0 == 0b0110:
                e0 = 0b0010
                continue
            elif e0 == 0b0010:
                e0 = 0b1010
                x, y = self.xmax, self.ymax
            elif e0 == 0b1010:
                e0 = 0b1000
                continue
            elif e0 == 0b1000:
                e0 = 0b1001
                x, y = self.xmin, self.ymax
            elif e0 == 0b1001:
                e0 = 0b0001
                continue
            elif e0 == 0b0001:
                e0 = 0b0101
                x, y = self.xmin, self.ymin
            else:
                break
            assert x is not None and y is not None
            if (j >= len(p) or p[j] != x or p[j + 1] != y) and self.contains(i, x, y):
                p.insert(j, x)
                p.insert(j, y)
                j += 2
        return j

    def _project(self, x0: float, y0: float, vx: float, vy: float) -> list[float] | None:
        t = float("inf")
        x = y = None
        if vy < 0:
            if y0 <= self.ymin:
                return None
            c = (self.ymin - y0) / vy
            if c < t:
                t = c
                y = self.ymin
                x = x0 + t * vx
        elif vy > 0:
            if y0 >= self.ymax:
                return None
            c = (self.ymax - y0) / vy
            if c < t:
                t = c
                y = self.ymax
                x = x0 + t * vx
        if vx > 0:
            if x0 >= self.xmax:
                return None
            c = (self.xmax - x0) / vx
            if c < t:
                t = c
                x = self.xmax
                y = y0 + t * vy
        elif vx < 0:
            if x0 <= self.xmin:
                return None
            c = (self.xmin - x0) / vx
            if c < t:
                t = c
                x = self.xmin
                y = y0 + t * vy
        if x is None or y is None:
            return None
        return [x, y]

    def _edgecode(self, x: float, y: float) -> int:
        ex = 0b0001 if x == self.xmin else 0b0010 if x == self.xmax else 0
        ey = 0b0100 if y == self.ymin else 0b1000 if y == self.ymax else 0
        return ex | ey

    def _regioncode(self, x: float, y: float) -> int:
        rx = 0b0001 if x < self.xmin else 0b0010 if x > self.xmax else 0
        ry = 0b0100 if y < self.ymin else 0b1000 if y > self.ymax else 0
        return rx | ry

    def _simplify(self, p: list[float] | None) -> list[float] | None:
        if not p or len(p) <= 4:
            return p
        while len(p) > 4:
            removed = False
            for i in range(0, len(p), 2):
                j = (i + 2) % len(p)
                k = (i + 4) % len(p)
                if (p[i] == p[j] == p[k]) or (p[i + 1] == p[j + 1] == p[k + 1]):
                    del p[j : j + 2]
                    removed = True
                    break
            if not removed:
                break
        if not len(p):  # pragma: no cover
            return None
        return p


__all__ = ["Voronoi"]
