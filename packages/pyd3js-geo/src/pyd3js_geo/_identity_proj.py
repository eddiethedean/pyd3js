"""Identity projection (d3-geo `projection/identity.js`)."""

from __future__ import annotations

import math
from typing import Any

_MISSING = object()
_MISSING_POST = object()


def geo_identity() -> Any:
    k = 1.0
    tx = ty = 0.0
    sx = sy = 1.0
    alpha = 0.0
    sa = 0.0
    ca = 1.0
    x0: float | None = None
    y0 = y1 = x1 = 0.0
    kx = ky = 1.0
    postclip: Any = None
    cache: Any = None
    cache_stream: Any = None

    def _identity_stream(s: Any) -> Any:
        return s

    postclip = _identity_stream

    def reset() -> Any:
        nonlocal kx, ky, cache, cache_stream
        kx = k * sx
        ky = k * sy
        cache = cache_stream = None
        return projection

    def projection(p: list[float]) -> list[float]:
        x = p[0] * kx
        y = p[1] * ky
        if alpha:
            t = y * ca - x * sa
            x = x * ca + y * sa
            y = t
        return [x + tx, y + ty]

    def invert(p: list[float]) -> list[float]:
        x = p[0] - tx
        y = p[1] - ty
        if alpha:
            t = y * ca + x * sa
            x = x * ca - y * sa
            y = t
        return [x / kx, y / ky]

    projection.invert = invert  # type: ignore[attr-defined]

    def stream(sink: Any) -> Any:
        nonlocal cache, cache_stream
        if cache is not None and cache_stream is sink:
            return cache
        cache_stream = sink
        from pyd3js_geo._core import transformer

        def point_fn(s: Any, x: float, y: float, z: Any = None) -> None:
            pxy = projection([x, y])
            if z is not None:
                s.stream.point(pxy[0], pxy[1], z)
            else:
                s.stream.point(pxy[0], pxy[1])

        transform = transformer({"point": point_fn})
        cache = transform(postclip(sink))
        return cache

    projection.stream = stream  # type: ignore[attr-defined]

    def postclip_method(v: Any = _MISSING_POST) -> Any:
        nonlocal postclip
        if v is _MISSING_POST:
            return postclip
        postclip = v
        return reset()

    projection.postclip = postclip_method  # type: ignore[attr-defined]

    def clip_extent(v: Any = _MISSING) -> Any:
        nonlocal postclip, x0, y0, x1, y1
        if v is _MISSING:
            return None if x0 is None else [[x0, y0], [x1, y1]]
        from pyd3js_geo.clip._rectangle import clip_rectangle

        if v is None:
            postclip = _identity_stream
            x0 = None
        else:
            postclip = clip_rectangle(
                float(v[0][0]),
                float(v[0][1]),
                float(v[1][0]),
                float(v[1][1]),
            )
            x0, y0 = float(v[0][0]), float(v[0][1])
            x1, y1 = float(v[1][0]), float(v[1][1])
        return reset()

    projection.clipExtent = clip_extent  # type: ignore[attr-defined]

    def scale(v: Any = _MISSING) -> Any:
        nonlocal k
        if v is _MISSING:
            return k
        k = float(v)
        return reset()

    def translate(v: Any = _MISSING) -> Any:
        nonlocal tx, ty
        if v is _MISSING:
            return [tx, ty]
        tx, ty = float(v[0]), float(v[1])
        return reset()

    def angle(v: Any = _MISSING) -> Any:
        nonlocal alpha, sa, ca
        if v is _MISSING:
            return alpha * 180 / math.pi
        alpha = math.radians(float(v) % 360)
        sa = math.sin(alpha)
        ca = math.cos(alpha)
        return reset()

    def reflect_x(v: Any = _MISSING) -> Any:
        nonlocal sx
        if v is _MISSING:
            return sx < 0
        sx = -1.0 if v else 1.0
        return reset()

    def reflect_y(v: Any = _MISSING) -> Any:
        nonlocal sy
        if v is _MISSING:
            return sy < 0
        sy = -1.0 if v else 1.0
        return reset()

    projection.scale = scale  # type: ignore[attr-defined]
    projection.translate = translate  # type: ignore[attr-defined]
    projection.angle = angle  # type: ignore[attr-defined]
    projection.reflectX = reflect_x  # type: ignore[attr-defined]
    projection.reflectY = reflect_y  # type: ignore[attr-defined]

    def fit_extent_fn(extent: list[list[float]], obj: Any) -> Any:
        from pyd3js_geo._core import fitExtent

        return fitExtent(projection, extent, obj)

    def fit_size_fn(size: list[float], obj: Any) -> Any:
        from pyd3js_geo._core import fitSize

        return fitSize(projection, size, obj)

    def fit_width_fn(width: float, obj: Any) -> Any:
        from pyd3js_geo._core import fitWidth

        return fitWidth(projection, width, obj)

    def fit_height_fn(height: float, obj: Any) -> Any:
        from pyd3js_geo._core import fitHeight

        return fitHeight(projection, height, obj)

    projection.fitExtent = fit_extent_fn  # type: ignore[attr-defined]
    projection.fitSize = fit_size_fn  # type: ignore[attr-defined]
    projection.fitWidth = fit_width_fn  # type: ignore[attr-defined]
    projection.fitHeight = fit_height_fn  # type: ignore[attr-defined]

    reset()
    return projection
