from __future__ import annotations

from typing import Any, Optional

from pyd3js_selection._dom import Document, Element, Window
import pyd3js_selection._globals as g
from pyd3js_selection.selection.index import Selection


def select(node: Any = None) -> Selection:
    if isinstance(node, str):
        if g.document is None:
            return Selection([[None]], [None])
        found = g.document.querySelector(node)
        return Selection([[found]], [g.document.documentElement])
    if node is None:
        return Selection([[node]], [None])
    if isinstance(node, (Document, Window, Element)) or isinstance(node, object):
        return Selection([[node]], [None])
    return Selection([[node]], [None])

