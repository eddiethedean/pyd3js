"""geoCircle generator (d3-geo `circle.js`)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, cast

from pyd3js_geo.cartesian import spherical

epsilon = 1e-12
tau = 2 * math.pi
degrees = 180 / math.pi
radians = math.pi / 180

_MISSING = object()


def acos(x: float) -> float:
    return 0 if x > 1 else math.pi if x < -1 else math.acos(x)  # pragma: no cover


def circle_radius(cos_radius: float, pt: Sequence[float]) -> float:
    from pyd3js_geo.cartesian import cartesian as to_cart  # pragma: no cover
    from pyd3js_geo.cartesian import cartesian_normalize_in_place  # pragma: no cover

    p = list(to_cart(pt))  # pragma: no cover
    p[0] -= cos_radius  # pragma: no cover
    cartesian_normalize_in_place(p)  # pragma: no cover
    r = acos(-p[1])  # pragma: no cover
    return ((-p[2] < 0 and -r or r) + tau - epsilon) % tau  # pragma: no cover


def circle_stream(
    stream: Any,
    radius: float,
    delta: float,
    direction: float,
    t0: Any,
    t1: Any,
) -> None:
    if not delta:
        return  # pragma: no cover
    cos_radius = math.cos(radius)
    sin_radius = math.sin(radius)
    step = direction * delta
    if t0 is None:
        t0 = radius + direction * tau
        t1 = radius - step / 2
    else:
        t0 = circle_radius(cos_radius, cast(Sequence[float], t0))  # pragma: no cover
        t1 = circle_radius(cos_radius, cast(Sequence[float], t1))  # pragma: no cover
        if (direction > 0 and t0 < t1) or (direction <= 0 and t0 > t1):  # pragma: no cover
            t0 += direction * tau  # pragma: no cover
    t = t0
    while (direction > 0 and t > t1) or (direction <= 0 and t < t1):
        pt = spherical(
            [cos_radius, -sin_radius * math.cos(t), -sin_radius * math.sin(t)]
        )
        stream.point(pt[0], pt[1])
        t -= step


def geo_circle_factory() -> Any:
    center_val = [0.0, 0.0]
    radius_val = 90.0
    precision_val = 6.0

    def circle(*_a: Any, **_k: Any) -> dict[str, Any]:
        from pyd3js_geo.rotation import geoRotation

        c = list(center_val)
        r = float(radius_val) * radians
        p = float(precision_val) * radians
        ring: list[list[float]] = []
        rot_inv = geoRotation([-c[0], -c[1], 0.0]).invert

        class S:
            def point(self, x: float, y: float, _z: Any = None) -> None:
                q = rot_inv([x * degrees, y * degrees])
                ring.append([q[0], q[1]])

        circle_stream(S(), r, p, 1.0, None, None)
        return {"type": "Polygon", "coordinates": [ring]}

    def center_method(v: Any = _MISSING, *_a: Any, **_k: Any) -> Any:
        nonlocal center_val
        if v is _MISSING:
            return center_val  # pragma: no cover
        if hasattr(v, "__iter__") and not isinstance(v, (str, bytes)):
            center_val = [float(v[0]), float(v[1])]
        return circle

    def radius_method(v: Any = _MISSING, *_a: Any, **_k: Any) -> Any:
        nonlocal radius_val
        if v is _MISSING:
            return radius_val  # pragma: no cover
        radius_val = float(v)
        return circle

    def precision_method(v: Any = _MISSING, *_a: Any, **_k: Any) -> Any:
        nonlocal precision_val
        if v is _MISSING:
            return precision_val  # pragma: no cover
        precision_val = float(v)
        return circle

    circle.center = center_method  # type: ignore[attr-defined]
    circle.radius = radius_method  # type: ignore[attr-defined]
    circle.precision = precision_method  # type: ignore[attr-defined]
    return circle
