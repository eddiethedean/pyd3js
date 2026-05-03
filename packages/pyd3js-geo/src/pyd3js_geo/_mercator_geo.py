"""Mercator / transverse-Mercator automatic clip (d3-geo `projection/mercator.js`)."""

from __future__ import annotations

import math
from typing import Any

pi = math.pi
_MISSING = object()


def wrap_mercator_projection(m: Any, is_mercator_raw: bool) -> Any:
    """Attach `reclip` behavior to scale/translate/center/clipExtent."""
    x0: float | None = None
    y0: float | None = None
    x1: float | None = None
    y1: float | None = None

    _scale = m.scale
    _translate = m.translate
    _center = m.center
    _clip_extent = m.clipExtent

    def reclip() -> Any:
        from pyd3js_geo._core import geoRotation

        k = pi * m.scale()
        inv = geoRotation(m.rotate()).invert([0.0, 0.0])  # type: ignore[attr-defined]
        t = m(inv)
        if x0 is None:
            ce = [[t[0] - k, t[1] - k], [t[0] + k, t[1] + k]]
        elif is_mercator_raw:
            ce = [
                [max(t[0] - k, x0), y0 if y0 is not None else 0.0],
                [min(t[0] + k, x1 if x1 is not None else 0.0), y1 if y1 is not None else 0.0],
            ]
        else:
            ce = [
                [x0 if x0 is not None else 0.0, max(t[1] - k, y0 if y0 is not None else 0.0)],
                [x1 if x1 is not None else 0.0, min(t[1] + k, y1 if y1 is not None else 0.0)],
            ]
        return _clip_extent(ce)

    def scale(v: Any = _MISSING) -> Any:
        if v is _MISSING:
            return _scale()
        _scale(v)
        return reclip()

    def translate(v: Any = _MISSING) -> Any:
        if v is _MISSING:
            return _translate()
        _translate(v)
        return reclip()

    def center(v: Any = _MISSING) -> Any:
        if v is _MISSING:
            return _center()
        _center(v)
        return reclip()

    def clip_extent(v: Any = _MISSING) -> Any:
        nonlocal x0, y0, x1, y1
        if v is _MISSING:
            return None if x0 is None else [[x0, y0], [x1, y1]]
        if v is None:
            x0 = y0 = x1 = y1 = None
        else:
            x0, y0 = float(v[0][0]), float(v[0][1])
            x1, y1 = float(v[1][0]), float(v[1][1])
        return reclip()

    m.scale = scale  # type: ignore[method-assign]
    m.translate = translate  # type: ignore[method-assign]
    m.center = center  # type: ignore[method-assign]
    m.clipExtent = clip_extent  # type: ignore[method-assign]
    return reclip()
