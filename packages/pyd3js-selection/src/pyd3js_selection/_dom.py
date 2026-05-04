from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Optional

HTML_NS = "http://www.w3.org/1999/xhtml"
SVG_NS = "http://www.w3.org/2000/svg"


@dataclass(eq=False)
class Node:
    parentNode: Optional["Element"] = None


@dataclass
class StyleDeclaration:
    _values: dict[str, str] = field(default_factory=dict)
    _priority: dict[str, str] = field(default_factory=dict)

    def getPropertyValue(self, name: str) -> str:
        return self._values.get(name, "")

    def getPropertyPriority(self, name: str) -> str:
        return self._priority.get(name, "")

    def setProperty(self, name: str, value: str, priority: str = "") -> None:
        self._values[name] = value
        self._priority[name] = priority or ""

    def removeProperty(self, name: str) -> None:
        self._values.pop(name, None)
        self._priority.pop(name, None)


@dataclass(eq=False)
class Element(Node):
    tagName: str = ""
    namespaceURI: str = HTML_NS
    attributes: dict[str, str] = field(default_factory=dict)
    style: StyleDeclaration = field(default_factory=StyleDeclaration)
    _children: list["Element"] = field(default_factory=list)
    _text: str = ""

    @property
    def childNodes(self) -> list["Element"]:
        return list(self._children)

    @property
    def textContent(self) -> str:
        if self._children:
            return "".join(c.textContent for c in self._children)
        return self._text

    @textContent.setter
    def textContent(self, value: str) -> None:
        self._children.clear()
        self._text = value

    def appendChild(self, child: "Element") -> "Element":
        # DOM move semantics: if already attached, detach first.
        if child.parentNode is not None and child.parentNode is not self:
            child.parentNode.removeChild(child)
        if child in self._children:
            self._children.remove(child)
        child.parentNode = self
        self._children.append(child)
        return child

    def insertBefore(
        self, child: "Element", next_sibling: Optional["Element"]
    ) -> "Element":
        if child.parentNode is not None and child.parentNode is not self:
            child.parentNode.removeChild(child)
        if (
            child.parentNode is self
            and next_sibling is not None
            and child in self._children
            and next_sibling in self._children
            and self._children.index(child) < self._children.index(next_sibling)
        ):
            # Already in the right place.
            return child
        insert_at = None
        if next_sibling is not None and next_sibling in self._children:
            insert_at = self._children.index(next_sibling)
            if child in self._children:
                # If moving within the same parent from before the reference node,
                # removing the child shifts the reference index left by one.
                child_at = self._children.index(child)
                if child_at < insert_at:
                    insert_at -= 1
        if child in self._children:
            self._children.remove(child)
        child.parentNode = self
        if insert_at is None:
            self._children.append(child)
        else:
            self._children.insert(insert_at, child)
        return child

    def removeChild(self, child: "Element") -> "Element":
        self._children.remove(child)
        child.parentNode = None
        return child

    @property
    def nextSibling(self) -> Optional["Element"]:
        if self.parentNode is None:
            return None
        sibs = self.parentNode._children
        try:
            i = sibs.index(self)
        except ValueError:
            return None
        return sibs[i + 1] if i + 1 < len(sibs) else None

    @property
    def firstChild(self) -> Optional["Element"]:
        return self._children[0] if self._children else None

    def getAttribute(self, name: str) -> Optional[str]:
        return self.attributes.get(name)

    def setAttribute(self, name: str, value: str) -> None:
        self.attributes[name] = value

    def removeAttribute(self, name: str) -> None:
        self.attributes.pop(name, None)

    def hasAttribute(self, name: str) -> bool:
        return name in self.attributes

    # Namespace variants (minimal): store as "{uri}:{name}" keys.
    def getAttributeNS(self, uri: str, name: str) -> Optional[str]:
        return self.attributes.get(f"{uri}:{name}")

    def setAttributeNS(self, uri: str, name: str, value: str) -> None:
        self.attributes[f"{uri}:{name}"] = value

    def removeAttributeNS(self, uri: str, name: str) -> None:
        self.attributes.pop(f"{uri}:{name}", None)

    def querySelector(self, selector: str) -> Optional["Element"]:
        matches = self.querySelectorAll(selector)
        return matches[0] if matches else None

    def querySelectorAll(self, selector: str) -> list["Element"]:
        # Minimal selector support for upstream tests: tag, #id, .class, tag.class,
        # and comma-separated unions (no descendant selectors).
        selector = selector.strip()
        parts = [s.strip() for s in selector.split(",") if s.strip()]
        out: list[Element] = []

        def visit(node: Element) -> None:
            for sel in parts:
                if _matches_selector(node, sel):
                    out.append(node)
                    break
            for c in node._children:
                visit(c)

        visit(self)
        return out

    @property
    def innerHTML(self) -> str:
        def esc(s: str) -> str:
            return (
                s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        def serialize(el: "Element") -> str:
            tag = el.tagName.lower()
            attrs = ""
            if el.attributes:
                parts = []
                for k, v in el.attributes.items():
                    if ":" in k:
                        continue
                    parts.append(f'{k}="{esc(v)}"')
                if parts:
                    attrs = " " + " ".join(parts)
            if el._children:
                inner = "".join(serialize(c) for c in el._children)
            else:
                inner = esc(el._text)
            return f"<{tag}{attrs}>{inner}</{tag}>"

        if self._children:
            return "".join(serialize(c) for c in self._children)
        return getattr(self, "_inner_html", "")

    @innerHTML.setter
    def innerHTML(self, value: str) -> None:
        setattr(self, "_inner_html", value)


def _matches_selector(el: Element, selector: str) -> bool:
    selector = selector.strip()
    # Very small CSS subset needed by upstream tests.
    last_child = False
    first_child = False
    if selector.endswith(":last-child"):
        last_child = True
        selector = selector[: -len(":last-child")]
    if selector.endswith(":first-child"):
        first_child = True
        selector = selector[: -len(":first-child")]

    if selector.startswith("[") and selector.endswith("]"):
        inner = selector[1:-1].strip()
        if "=" in inner:
            k, v = inner.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            ok = el.attributes.get(k) == v
        else:
            ok = inner in el.attributes
    elif selector.startswith("#"):
        ok = el.attributes.get("id") == selector[1:]
    elif selector == "*":
        ok = True
    elif selector.startswith("."):
        cls = el.attributes.get("class", "")
        ok = selector[1:] in cls.split()
    elif "." in selector:
        tag, cls = selector.split(".", 1)
        if el.tagName.lower() != tag.lower():
            ok = False
        else:
            classes = el.attributes.get("class", "")
            ok = cls in classes.split()
    elif selector == "":
        ok = False
    else:
        ok = el.tagName.lower() == selector.lower()

    if not ok:
        return False
    if last_child:
        parent = getattr(el, "parentNode", None)
        if parent is None:
            return False
        children = getattr(parent, "childNodes", [])
        return len(children) > 0 and children[-1] is el
    if first_child:
        parent = getattr(el, "parentNode", None)
        if parent is None:
            return False
        children = getattr(parent, "childNodes", [])
        return len(children) > 0 and children[0] is el
    return True


@dataclass
class Document(Node):
    documentElement: Element = field(
        default_factory=lambda: Element(tagName="HTML", namespaceURI=HTML_NS)
    )
    body: Element = field(
        default_factory=lambda: Element(tagName="BODY", namespaceURI=HTML_NS)
    )

    def __post_init__(self) -> None:
        self.documentElement.appendChild(self.body)
        # Mirror browser: body.innerHTML serializes its children.

    @property
    def defaultView(self) -> "Window":
        return Window(self)

    def querySelector(self, selector: str) -> Optional[Element]:
        return self.documentElement.querySelector(selector)

    def querySelectorAll(self, selector: str) -> list[Element]:
        return self.documentElement.querySelectorAll(selector)

    def createElementNS(self, namespace: str, name: str) -> Element:
        tag = name.upper() if namespace == HTML_NS else name
        return Element(tagName=tag, namespaceURI=namespace)

    def createElement(self, name: str) -> Element:
        return self.createElementNS(HTML_NS, name)


@dataclass
class Window:
    document: Document


class _HTMLToDOM(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.document = Document()
        self._stack: list[Element] = [self.document.body]
        self._in_svg = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        if t == "svg":
            self._in_svg = True
        # Reuse the built-in document elements for <html> and <body>.
        if t == "html":
            el = self.document.documentElement
        elif t == "body":
            el = self.document.body
        else:
            ns = SVG_NS if self._in_svg else HTML_NS
            el = self.document.createElementNS(ns, tag)
            self._stack[-1].appendChild(el)
        for k, v in attrs:
            if v is None:
                continue
            el.setAttribute(k, v)
        self._stack.append(el)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if len(self._stack) > 1:
            self._stack.pop()
        if t == "svg":
            self._in_svg = False

    def handle_data(self, data: str) -> None:
        if data.strip() == "":
            return
        # Attach to current element as text.
        self._stack[-1]._text += data


def parse_html(html: str) -> Document:
    p = _HTMLToDOM()
    p.feed(html or "")
    p.close()
    return p.document
