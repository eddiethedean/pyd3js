from __future__ import annotations

from typing import Any, Optional


def styleValue(node: Any, name: str) -> Optional[str]:
    if node is None:
        return None
    if hasattr(node, "style") and isinstance(getattr(node, "style"), dict):
        return getattr(node, "style").get(name)
    return None


style = styleValue

