from __future__ import annotations

from collections.abc import Callable
from typing import Optional

from pyd3js_selection._dom import HTML_NS, Document, Element, SVG_NS
import pyd3js_selection._globals as g
from pyd3js_selection.namespace import namespace


def creator(name: str) -> Callable[[Optional[Element]], Element]:
    ns_info = namespace(name)
    if isinstance(ns_info, dict):
        ns = ns_info["space"]
        local = ns_info["local"]
    else:
        ns = None
        local = ns_info

    if ns is None:
        # Inherit from context element if possible; else infer svg tag.
        def _infer(this: Optional[Element]) -> str:
            if this is not None and getattr(this, "namespaceURI", None):
                return this.namespaceURI
            return SVG_NS if str(local).lower() == "svg" else HTML_NS

    else:
        def _infer(this: Optional[Element]) -> str:  # noqa: ARG001
            return ns

    def _create(this: Optional[Element]) -> Element:
        doc: Optional[Document] = g.document
        if doc is None:
            doc = Document()
        space = _infer(this)
        if space == HTML_NS and hasattr(doc, "createElement"):
            return doc.createElement(str(local))
        return doc.createElementNS(space, str(local))

    return _create

