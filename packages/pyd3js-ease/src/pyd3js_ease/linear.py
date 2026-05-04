from __future__ import annotations

from typing import Any

from pyd3js_ease._coerce import ease_t


def easeLinear(t: Any) -> float:
    return ease_t(t)


__all__ = ["easeLinear"]
