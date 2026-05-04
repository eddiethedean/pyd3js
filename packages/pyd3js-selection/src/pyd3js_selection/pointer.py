from __future__ import annotations

from typing import Any, Optional


def pointer(event: Any, target: Optional[Any] = None) -> list[float]:
    # Minimal parity for upstream tests: return [pageX, pageY] or [clientX, clientY]
    if hasattr(event, "clientX") and hasattr(event, "clientY"):
        return [float(getattr(event, "clientX")), float(getattr(event, "clientY"))]
    if isinstance(event, dict):
        if "clientX" in event and "clientY" in event:
            return [float(event["clientX"]), float(event["clientY"])]
        if "pageX" in event and "pageY" in event:
            return [float(event["pageX"]), float(event["pageY"])]
    return [0.0, 0.0]
