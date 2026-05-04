from __future__ import annotations

from typing import Any

import pyd3js_selection._globals as g
from pyd3js_selection.selection.index import Selection


def selectAll(selector: Any = None) -> Selection:
    if isinstance(selector, str):
        if g.document is None:
            return Selection([[]], [None])
        nodes = g.document.querySelectorAll(selector)
        return Selection([nodes], [g.document.documentElement])
    if selector is None:
        return Selection([[]], [None])
    if isinstance(selector, (list, tuple)):
        return Selection([list(selector)], [None])
    return Selection([[selector]], [None])
