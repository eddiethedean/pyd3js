from __future__ import annotations

from typing import Any, Optional

from pyd3js_selection.pointer import pointer


def pointers(event: Any, target: Optional[Any] = None) -> list[list[float]]:
    if isinstance(event, dict) and "touches" in event:
        return [pointer(t, target) for t in event["touches"]]
    if isinstance(event, list):
        return [pointer(t, target) for t in event]
    return [pointer(event, target)]

