from __future__ import annotations

import threading
from typing import Any

import pyd3js_selection as s

from pyd3js_drag.noevent import noevent


def dragDisable(view: Any) -> None:
    # Port of d3-drag/src/nodrag.js
    if isinstance(view, dict):
        doc = view.get("document")
        root = (
            doc.get("documentElement")
            if isinstance(doc, dict)
            else getattr(doc, "documentElement", None)
        )
    else:
        root = view.document.documentElement
    sel = s.select(view).on("dragstart.drag", noevent, True)
    if hasattr(root, "onselectstart") or (
        isinstance(root, dict) and "onselectstart" in root
    ):
        sel.on("selectstart.drag", noevent, True)
    else:
        # Firefox fallback: temporarily set MozUserSelect.
        style = (
            root["style"] if isinstance(root, dict) else getattr(root, "style", None)
        )
        if style is not None:
            prev = getattr(style, "MozUserSelect", None)
            setattr(root, "__noselect", prev)
            setattr(style, "MozUserSelect", "none")


def dragEnable(view: Any, noclick: bool = False) -> None:
    if isinstance(view, dict):
        doc = view.get("document")
        root = (
            doc.get("documentElement")
            if isinstance(doc, dict)
            else getattr(doc, "documentElement", None)
        )
    else:
        root = view.document.documentElement
    sel = s.select(view).on("dragstart.drag", None)
    if noclick:
        sel.on("click.drag", noevent, True)

        def _clear() -> None:
            try:
                s.select(view).on("click.drag", None)
            except Exception:  # noqa: BLE001
                pass

        threading.Timer(0, _clear).start()

    if hasattr(root, "onselectstart") or (
        isinstance(root, dict) and "onselectstart" in root
    ):
        sel.on("selectstart.drag", None)
    else:
        style = (
            root["style"] if isinstance(root, dict) else getattr(root, "style", None)
        )
        prev = getattr(root, "__noselect", None)
        if style is not None:
            setattr(style, "MozUserSelect", prev)
        if hasattr(root, "__dict__") and "__noselect" in root.__dict__:
            del root.__dict__["__noselect"]
        elif isinstance(root, dict):
            root.pop("__noselect", None)
