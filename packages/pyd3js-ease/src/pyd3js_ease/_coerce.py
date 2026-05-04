from __future__ import annotations

from typing import Any


def ease_t(t: Any) -> float:
    """Coerce *t* like JavaScript unary `+` / `valueOf` (d3-ease tests)."""
    vo = getattr(t, "valueOf", None)
    if callable(vo) and not isinstance(t, (int, float, str, bool)):
        return ease_t(vo())
    return float(t)
