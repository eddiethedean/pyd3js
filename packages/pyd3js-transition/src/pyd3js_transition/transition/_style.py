from __future__ import annotations

from typing import Any


def style_value(node: Any, name: str) -> str | None:
    if node is None:
        return None
    # d3-selection port uses `style` as dict in tests.
    if hasattr(node, "style") and isinstance(getattr(node, "style"), dict):
        return getattr(node, "style").get(name)
    return None


def style_set(node: Any, name: str, value: Any, priority: str = "") -> None:
    if node is None:
        return
    if hasattr(node, "style") and isinstance(getattr(node, "style"), dict):
        getattr(node, "style")[name] = None if value is None else str(value)
        return
    style_obj = getattr(node, "style", None)
    if style_obj is not None and hasattr(style_obj, "setProperty"):
        style_obj.setProperty(name, str(value), priority)


def style_remove(node: Any, name: str) -> None:
    if node is None:
        return
    if hasattr(node, "style") and isinstance(getattr(node, "style"), dict):
        getattr(node, "style").pop(name, None)
        return
    style_obj = getattr(node, "style", None)
    if style_obj is not None and hasattr(style_obj, "removeProperty"):
        style_obj.removeProperty(name)

