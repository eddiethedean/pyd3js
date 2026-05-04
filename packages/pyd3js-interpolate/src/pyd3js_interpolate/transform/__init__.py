"""Transform interpolation — port of d3-interpolate `transform/index.js`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_interpolate.number import interpolate_number
from pyd3js_interpolate.transform.parse import parse_css, parse_svg


def _rotate_shortest(a0: float, b0: float) -> tuple[float, float]:
    if a0 != b0:
        if a0 - b0 > 180:
            b0 += 360.0
        elif b0 - a0 > 180:
            a0 += 360.0
    return a0, b0


def _interpolate_transform(
    parse: Callable[[Any], dict[str, float]],
    px_comma: str,
    px_paren: str,
    deg_paren: str,
) -> Callable[[Any, Any], Callable[[float], str]]:
    def interpolate(a: Any, b: Any) -> Callable[[float], str]:
        s: list[str | None] = []
        q: list[tuple[int, Callable[[float], float]]] = []

        def pop() -> str:
            return (s.pop() + " ") if s else ""

        def translate_fn(xa: float, ya: float, xb: float, yb: float) -> None:
            if xa != xb or ya != yb:
                s.extend(["translate(", None, px_comma, None, px_paren])
                ln = len(s)
                q.append((ln - 4, interpolate_number(xa, xb)))
                q.append((ln - 2, interpolate_number(ya, yb)))
            elif xb or yb:
                s.append(f"translate({xb}{px_comma}{yb}{px_paren}")

        def rotate_fn(a0: float, b0: float) -> None:
            if a0 != b0:
                a0, b0 = _rotate_shortest(a0, b0)
                s.append(pop() + "rotate(")
                s.extend([None, deg_paren])
                q.append((len(s) - 2, interpolate_number(a0, b0)))
            elif b0:
                s.append(pop() + f"rotate({b0}{deg_paren}")

        def skew_x_fn(a0: float, b0: float) -> None:
            if a0 != b0:
                s.append(pop() + "skewX(")
                s.extend([None, deg_paren])
                q.append((len(s) - 2, interpolate_number(a0, b0)))
            elif b0:
                s.append(pop() + f"skewX({b0}{deg_paren}")

        def scale_fn(xa: float, ya: float, xb: float, yb: float) -> None:
            if xa != xb or ya != yb:
                s.append(pop() + "scale(")
                s.extend([None, ",", None, ")"])
                ln = len(s)
                q.append((ln - 4, interpolate_number(xa, xb)))
                q.append((ln - 2, interpolate_number(ya, yb)))
            elif xb != 1 or yb != 1:
                s.append(pop() + f"scale({xb},{yb})")

        pa = parse(a)
        pb = parse(b)
        translate_fn(
            pa["translateX"], pa["translateY"], pb["translateX"], pb["translateY"]
        )
        rotate_fn(pa["rotate"], pb["rotate"])
        skew_x_fn(pa["skewX"], pb["skewX"])
        scale_fn(pa["scaleX"], pa["scaleY"], pb["scaleX"], pb["scaleY"])

        def f(t: float) -> str:
            out = [("" if x is None else x) for x in s]
            for idx, itp in q:
                out[idx] = str(itp(t))
            return "".join(out)

        return f

    return interpolate


interpolate_transform_css = _interpolate_transform(parse_css, "px, ", "px)", "deg)")
interpolate_transform_svg = _interpolate_transform(parse_svg, ", ", ")", ")")

__all__ = ["interpolate_transform_css", "interpolate_transform_svg"]
