"""
pyd3js-selection — Python port of d3-selection.
"""

from __future__ import annotations

from pyd3js_selection._globals import window
from pyd3js_selection.create import create
from pyd3js_selection.creator import creator
from pyd3js_selection.local import local
from pyd3js_selection.matcher import matcher
from pyd3js_selection.namespace import namespace
from pyd3js_selection.namespaces import namespaces
from pyd3js_selection.pointer import pointer
from pyd3js_selection.pointers import pointers
from pyd3js_selection.select import select
from pyd3js_selection.selectAll import selectAll
from pyd3js_selection.selection.index import Selection, selection
from pyd3js_selection.selector import selector
from pyd3js_selection.selectorAll import selectorAll
from pyd3js_selection.selection.style import style

__version__ = "0.0.0"

__all__ = (
    "__version__",
    "create",
    "creator",
    "document",
    "local",
    "matcher",
    "namespace",
    "namespaces",
    "pointer",
    "pointers",
    "select",
    "selectAll",
    "Selection",
    "selection",
    "selector",
    "selectorAll",
    "style",
    "window",
)

# Re-export the mutable global `document` handle (test fixtures set this).
def __getattr__(name: str):  # noqa: ANN001
    if name == "document":
        import pyd3js_selection._globals as _g

        return _g.document
    raise AttributeError(name)
