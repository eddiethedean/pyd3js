from __future__ import annotations

from typing import Any

import pyd3js_drag as d
from pyd3js_selection._dom import Document, Element


def test_exports() -> None:
    assert callable(d.drag)
    assert d.DragEvent is not None
    assert callable(d.dragDisable)
    assert callable(d.dragEnable)


def test_drag_mouse_gesture_dispatches_start_drag_end() -> None:
    doc = Document()
    parent = doc.body
    node = Element(tagName="DIV")
    parent.appendChild(node)

    # Provide minimal add/removeEventListener so Selection.on hooks don't explode.
    def _add(_typ, _listener, _capture=False):  # noqa: ANN001
        return None

    def _rm(_typ, _listener, _capture=False):  # noqa: ANN001
        return None

    win: dict[str, Any] = {
        "document": doc,
        "addEventListener": _add,
        "removeEventListener": _rm,
    }

    behavior = d.drag()
    events: list[tuple[str, float, float, float, float]] = []

    def started(this, event, datum):  # noqa: ANN001
        assert this is node
        events.append((event.type, event.x, event.y, event.dx, event.dy))

    def dragged(this, event, datum):  # noqa: ANN001
        events.append((event.type, event.x, event.y, event.dx, event.dy))

    def ended(this, event, datum):  # noqa: ANN001
        events.append((event.type, event.x, event.y, event.dx, event.dy))

    behavior.on("start", started).on("drag", dragged).on("end", ended)

    # Apply to a one-node selection.
    import pyd3js_selection as s

    sel = s.select(node)
    sel.call(behavior)

    # Fire mousedown on node -> handlers are stored on node.__on by selection.on.
    mousedown = {
        "view": win,
        "clientX": 10,
        "clientY": 20,
        "ctrlKey": False,
        "button": 0,
        "preventDefault": lambda: None,
        "stopImmediatePropagation": lambda: None,
    }
    mousemove = {
        "view": win,
        "clientX": 13,
        "clientY": 24,
        "preventDefault": lambda: None,
        "stopImmediatePropagation": lambda: None,
    }
    mouseup = {
        "view": win,
        "clientX": 13,
        "clientY": 24,
        "preventDefault": lambda: None,
        "stopImmediatePropagation": lambda: None,
    }

    # Invoke listener functions directly from the stored __on table.
    ons = node.__dict__["__on"]
    down = [o for o in ons if o["type"] == "mousedown"][0]["listener"]
    down(node, mousedown, None)

    wons = win["__on"]  # type: ignore[index]
    move = [o for o in wons if o["type"] == "mousemove"][0]["listener"]
    up = [o for o in wons if o["type"] == "mouseup"][0]["listener"]
    move(win, mousemove, None)
    up(win, mouseup, None)

    assert [t for (t, *_rest) in events] == ["start", "drag", "end"]
