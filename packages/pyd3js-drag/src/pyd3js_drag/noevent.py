from __future__ import annotations

from typing import Any


# In JS these are listener option dicts; in Python we only model capture.
nonpassive: dict[str, Any] = {"passive": False}
nonpassivecapture: dict[str, Any] = {"capture": True, "passive": False}


def _maybe_call(obj: Any, name: str) -> None:
    if obj is None:
        return
    if hasattr(obj, name):
        getattr(obj, name)()
        return
    if isinstance(obj, dict) and callable(obj.get(name)):
        obj[name]()


def nopropagation(event: Any) -> None:
    _maybe_call(event, "stopImmediatePropagation")


def noevent(event: Any) -> None:
    _maybe_call(event, "preventDefault")
    _maybe_call(event, "stopImmediatePropagation")
