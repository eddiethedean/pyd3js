"""Segment rejoin after clipping (d3-geo `clip/rejoin.js`)."""

from __future__ import annotations

import functools
from typing import Any, Callable

from pyd3js_geo._point_equal import point_equal

epsilon = 1e-6


class _Intersection:
    __slots__ = ("x", "z", "o", "e", "v", "n", "p")

    def __init__(
        self,
        point: list[float | None],
        points: list[list[float | None]] | None,
        other: "_Intersection | None",
        entry: bool,
    ) -> None:
        self.x = point
        self.z = points
        self.o = other
        self.e = entry
        self.v = False
        self.n: _Intersection | None = None
        self.p: _Intersection | None = None


def _link(array: list[_Intersection]) -> None:
    n = len(array)
    if not n:
        return  # pragma: no cover
    a = array[0]
    for i in range(1, n):
        b = array[i]
        a.n = b
        b.p = a
        a = b
    a.n = b = array[0]
    b.p = a


def clip_rejoin(
    segments: list[list[list[float | None]]],
    compare_intersection: Callable[[_Intersection, _Intersection], int],
    start_inside: bool | int,
    interpolate: Callable[[Any, Any, float, Any], None],
    stream: Any,
) -> None:
    subject: list[_Intersection] = []
    clip_list: list[_Intersection] = []

    for segment in segments:
        n = len(segment) - 1
        if n <= 0:
            continue  # pragma: no cover
        p0 = segment[0]
        p1 = segment[n]

        if point_equal(p0, p1):
            p0_2 = p0[2] if len(p0) > 2 else None
            p1_2 = p1[2] if len(p1) > 2 else None
            if not p0_2 and not p1_2:
                stream.lineStart()
                for i in range(n):
                    p0 = segment[i]
                    stream.point(p0[0], p0[1])
                stream.lineEnd()
                continue
            if p1[0] is not None:  # pragma: no cover
                p1[0] += 2 * epsilon  # pragma: no cover

        x_s = _Intersection(p0, segment, None, True)
        x_c = _Intersection(p0, None, x_s, False)
        x_s.o = x_c
        subject.append(x_s)
        clip_list.append(x_c)

        x_s2 = _Intersection(p1, segment, None, False)
        x_c2 = _Intersection(p1, None, x_s2, True)
        x_s2.o = x_c2
        subject.append(x_s2)
        clip_list.append(x_c2)

    if not subject:
        return

    clip_list.sort(key=functools.cmp_to_key(lambda a, b: compare_intersection(a, b)))
    _link(subject)
    _link(clip_list)

    si = start_inside
    for i in range(len(clip_list)):
        clip_list[i].e = si = not si

    start = subject[0]
    while True:
        current = start
        is_subject = True
        while current.v:
            current = current.n
            assert current is not None
            if current is start:
                return
        points = current.z
        stream.lineStart()
        while True:
            current.v = True
            assert current.o is not None
            current.o.v = True
            if current.e:
                if is_subject:
                    assert points is not None
                    for i in range(len(points)):
                        point = points[i]
                        stream.point(point[0], point[1])
                else:
                    assert current.n is not None
                    interpolate(current.x, current.n.x, 1.0, stream)
                current = current.n
            else:
                if is_subject:
                    assert current.p is not None  # pragma: no cover
                    points = current.p.z  # pragma: no cover
                    assert points is not None  # pragma: no cover
                    for i in range(len(points) - 1, -1, -1):  # pragma: no cover
                        point = points[i]  # pragma: no cover
                        stream.point(point[0], point[1])  # pragma: no cover
                else:
                    assert current.p is not None
                    interpolate(current.x, current.p.x, -1.0, stream)
                current = current.p
            assert current is not None
            assert current.o is not None
            current = current.o
            points = current.z
            is_subject = not is_subject
            if current.v:
                break
        stream.lineEnd()
