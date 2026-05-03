"""Function composition (d3-geo `compose.js`)."""

from __future__ import annotations

from typing import Any, Callable


def compose(a: Callable[..., Any], b: Callable[..., Any]) -> Callable[..., Any]:
    def c(*args: Any) -> Any:
        return b(*a(*args))

    if hasattr(a, "invert") and hasattr(b, "invert"):
        c.invert = lambda *args: a.invert(*b.invert(*args))  # type: ignore[attr-defined]
    return c


def geo_compose_project(
    a: Callable[[float, float], list[float]],
    b: Callable[[float, float], list[float]],
) -> Callable[[float, float], list[float]]:
    """d3-geo `compose.js` for forward projections (a then b on [x,y] pairs)."""

    def composed(x: float, y: float) -> list[float]:
        t = a(x, y)
        return b(t[0], t[1])

    if hasattr(a, "invert") and hasattr(b, "invert"):
        def inv(x: float, y: float) -> list[float] | None:
            t = b.invert(x, y)
            if t is None:
                return None
            return a.invert(t[0], t[1])  # type: ignore[misc]

        composed.invert = inv  # type: ignore[attr-defined]
    return composed
