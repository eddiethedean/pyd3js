from __future__ import annotations

from typing import Any


def easeLinear(t: Any) -> float:
    vo = getattr(t, "valueOf", None)
    if callable(vo) and not isinstance(t, (int, float, str, bool)):
        return easeLinear(vo())
    return float(t)


__all__ = ["easeLinear"]
