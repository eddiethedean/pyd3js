from __future__ import annotations

from pyd3js_selection.creator import creator
from pyd3js_selection.selection.index import Selection


def create(name: str) -> Selection:
    c = creator(name)
    node = c(None)
    return Selection([[node]], [None])

