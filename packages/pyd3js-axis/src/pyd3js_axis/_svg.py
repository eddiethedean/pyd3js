"""Minimal SVG element tree; outerHTML-style serialization (browser-like)."""

from __future__ import annotations

import html
from dataclasses import dataclass, field


@dataclass
class Element:
    tag: str
    parent: Element | None = None
    # Ordered attribute name/value; duplicate names allowed (d3 can set then overwrite).
    attrs: list[tuple[str, str]] = field(default_factory=list)
    children: list["Element"] = field(default_factory=list)
    # Text *inside* element, e.g. <text>0.0</text> (d3's text content).
    text_content: str = ""
    __data__: object | None = None
    # Mirror d3-axis/axis.js storing position function on the container.
    d3__axis: object | None = None
    # JS uses __axis on the selection node
    __axis: object | None = None

    def get_attribute(self, name: str) -> str | None:
        for n, v in self.attrs:
            if n == name:
                return v
        return None

    def set_attribute(self, name: str, value: str | None) -> None:
        if value is None:
            self._remove_attr(name)
            return
        # Replace last occurrence, else append (d3 re-sets the same name often).
        for k in range(len(self.attrs) - 1, -1, -1):
            n, _ = self.attrs[k]
            if n == name:
                self.attrs[k] = (n, str(value))
                return
        self.attrs.append((name, str(value)))

    def _remove_attr(self, name: str) -> None:
        self.attrs = [pair for pair in self.attrs if pair[0] != name]

    def remove_attribute(self, name: str) -> None:
        self._remove_attr(name)

    def has_class(self, cls: str) -> bool:
        a = self.get_attribute("class")
        if a is None:
            return False
        return cls in a.split()

    def append_child(self, child: Element) -> Element:
        if child.parent is not None:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: Element) -> None:
        if child in self.children:
            self.children.remove(child)
        child.parent = None

    def insert_before(self, new_child: Element, before: Element | None) -> Element:
        if before is None:
            return self.append_child(new_child)
        try:
            insert_idx = self.children.index(before)
        except ValueError:
            return self.append_child(new_child)
        old_parent = new_child.parent
        if old_parent is not None:
            old_parent.remove_child(new_child)
            if old_parent is self:
                insert_idx = self.children.index(before)
        new_child.parent = self
        self.children.insert(insert_idx, new_child)
        return new_child

    def query_selector(self, sel: str) -> Element | None:
        for el in _walk_depth_first(self):
            if _matches_selector_first(el, sel) and el is not self:  # noqa: SIM202
                return el
        return None

    def query_selector_all(self, sel: str) -> list[Element]:
        out: list[Element] = []
        for el in _walk_depth_first(self):
            if el is not self and _matches_selector_first(el, sel):
                out.append(el)
        return out


def _walk_depth_first(root: Element) -> list[Element]:
    out: list[Element] = [root]
    for ch in list(root.children):
        out.extend(_walk_depth_first(ch))
    return out


def _matches_selector_first(node: Element, sel: str) -> bool:
    s = sel.strip()
    if s.startswith("."):
        return node.has_class(s[1:])
    if s.startswith("#"):
        return (node.get_attribute("id") or "") == s[1:]
    return node.tag == s  # "line", "text", "path", "g"


def outer_html(node: Element) -> str:
    """Return HTML-like `outerHTML` (matches jsdom/Chrome ordering used in d3 tests)."""
    a_str = " ".join(f'{n}="{html.escape(v, quote=True)}"' for n, v in node.attrs)
    open_ = f"<{node.tag}"
    if a_str:
        open_ += " " + a_str
    open_ += ">"
    inner: list[str] = [open_]
    for ch in node.children:
        inner.append(outer_html(ch))
    if node.text_content and not node.children:
        inner.append(html.escape(node.text_content, quote=False))
    inner.append(f"</{node.tag}>")
    return "".join(inner)
