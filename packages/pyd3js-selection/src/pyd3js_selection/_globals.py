from __future__ import annotations

from typing import Optional

from pyd3js_selection._dom import Document, Window

# These mimic the global `document` / `window` that d3-selection expects in JS.
# Tests can replace them via the pytest fixture in package_tests.
document: Optional[Document] = None


def window(node) -> Optional[Window]:
    if isinstance(node, Window):
        return node
    if isinstance(node, Document):
        return node.defaultView
    # For our minimal DOM, everything lives under the module-level document.
    if document is None:
        return None
    return document.defaultView

