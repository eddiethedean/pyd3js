"""Access transition schedule dicts on nodes (JS ``__transition`` vs Python ``__transition__``)."""

from __future__ import annotations

from typing import Any


def schedules_get(node: Any) -> dict[Any, Any] | None:
    """Return the transition schedule dict on ``node``, if any."""
    return getattr(node, "__transition__", None) or getattr(node, "__transition", None)


def schedules_try_del(node: Any) -> None:
    """Remove schedule storage from ``node`` if present (either attribute name)."""
    for attr in ("__transition__", "__transition"):
        try:
            delattr(node, attr)
        except Exception:
            pass
