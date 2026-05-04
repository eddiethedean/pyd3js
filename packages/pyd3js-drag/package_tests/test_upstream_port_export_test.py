from __future__ import annotations

import pyd3js_drag as d3


def test_drag_methods_exported() -> None:
    assert sorted([k for k in d3.__all__ if not k.startswith("__")]) == [
        "DragEvent",
        "drag",
        "dragDisable",
        "dragEnable",
    ]
