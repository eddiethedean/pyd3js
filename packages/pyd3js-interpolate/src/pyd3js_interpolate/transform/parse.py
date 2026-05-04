"""Parse CSS/SVG transforms — port of d3-interpolate `transform/parse.js` (partial, no DOM)."""

from __future__ import annotations

import math
import re
from typing import Any

from pyd3js_interpolate.transform.decompose import IDENTITY, decompose

_FUN = re.compile(
    r"(matrix|translate|translateX|translateY|scale|rotate|skewX|skewY)\(([^)]*)\)",
    re.IGNORECASE,
)


def _strip_unit(token: str) -> float:
    t = token.strip()
    for suf in ("px", "deg", "rad", "em"):
        if t.lower().endswith(suf):
            t = t[: -len(suf)]
            break
    return float(t)


def _mul(
    a1: float,
    b1: float,
    c1: float,
    d1: float,
    e1: float,
    f1: float,
    a2: float,
    b2: float,
    c2: float,
    d2: float,
    e2: float,
    f2: float,
) -> tuple[float, float, float, float, float, float]:
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def _eye() -> tuple[float, float, float, float, float, float]:
    return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _mat_translate(
    tx: float, ty: float
) -> tuple[float, float, float, float, float, float]:
    return (1.0, 0.0, 0.0, 1.0, tx, ty)


def _mat_rotate_deg(deg: float) -> tuple[float, float, float, float, float, float]:
    rad = deg * math.pi / 180.0
    cos = math.cos(rad)
    sin = math.sin(rad)
    return (cos, sin, -sin, cos, 0.0, 0.0)


def _mat_scale(sx: float, sy: float) -> tuple[float, float, float, float, float, float]:
    return (sx, 0.0, 0.0, sy, 0.0, 0.0)


def _mat_skew_x(deg: float) -> tuple[float, float, float, float, float, float]:
    t = math.tan(deg * math.pi / 180.0)
    return (1.0, 0.0, t, 1.0, 0.0, 0.0)


def _mat_skew_y(deg: float) -> tuple[float, float, float, float, float, float]:
    t = math.tan(deg * math.pi / 180.0)
    return (1.0, t, 0.0, 1.0, 0.0, 0.0)


def _parse_fn(name: str, inner: str) -> tuple[float, float, float, float, float, float]:
    raw = [p.strip() for p in re.split(r"[,\s]+", inner.strip()) if p.strip()]
    n = name.lower()
    if n == "matrix":
        v = [float(x) for x in raw]
        if len(v) != 6:
            return _eye()
        return (v[0], v[1], v[2], v[3], v[4], v[5])
    if n == "translate":
        if not raw:
            return _eye()
        tx = _strip_unit(raw[0])
        ty = _strip_unit(raw[1]) if len(raw) > 1 else 0.0
        return _mat_translate(tx, ty)
    if n == "translatex":
        return _mat_translate(_strip_unit(raw[0]), 0.0) if raw else _eye()
    if n == "translatey":
        return _mat_translate(0.0, _strip_unit(raw[0])) if raw else _eye()
    if n == "scale":
        if not raw:
            return _eye()
        sx = _strip_unit(raw[0])
        sy = _strip_unit(raw[1]) if len(raw) > 1 else sx
        return _mat_scale(sx, sy)
    if n == "rotate":
        if not raw:
            return _eye()
        deg = _strip_unit(raw[0])
        if len(raw) >= 3:
            cx = _strip_unit(raw[1])
            cy = _strip_unit(raw[2])
            m1 = _mul(*_mat_translate(cx, cy), *_mat_rotate_deg(deg))
            return _mul(*m1, *_mat_translate(-cx, -cy))
        return _mat_rotate_deg(deg)
    if n == "skewx":
        return _mat_skew_x(_strip_unit(raw[0])) if raw else _eye()
    if n == "skewy":
        return _mat_skew_y(_strip_unit(raw[0])) if raw else _eye()
    return _eye()  # pragma: no cover


def parse_css(value: Any) -> dict[str, float]:
    s = str(value or "").strip()
    if not s:
        return dict(IDENTITY)
    acc = _eye()
    for m in _FUN.finditer(s):
        name, inner = m.group(1), m.group(2)
        acc = _mul(*acc, *_parse_fn(name, inner))
    return decompose(*acc)


def parse_svg(value: Any) -> dict[str, float]:
    """Parse an SVG `transform` attribute the same way as CSS (affine product, then decompose).

    Pure-Python approximation of `parseSvg` in d3-interpolate (no SVG DOM); matches
    `parse_css` for standard transform functions so `interpolateTransformSvg` tracks
    `interpolateTransformCss` for the same transform list.
    """
    if value is None or value == "":
        return dict(IDENTITY)
    s = str(value).strip()
    if not s:
        return dict(IDENTITY)
    acc = _eye()
    for m in _FUN.finditer(s):
        acc = _mul(*acc, *_parse_fn(m.group(1), m.group(2)))
    return decompose(*acc)


__all__ = ["parse_css", "parse_svg"]
