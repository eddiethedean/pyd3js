from __future__ import annotations

from types import SimpleNamespace

import pyd3js_selection as s
from pyd3js_selection._dom import Document, Element, StyleDeclaration, parse_html
from pyd3js_selection.local import local
from pyd3js_selection.matcher import matcher
from pyd3js_selection.namespace import namespace
from pyd3js_selection.selection import style as style_mod


def test_local_get_set_remove_to_string() -> None:
    loc = local()
    node = SimpleNamespace()
    assert loc.get(node) is None
    assert loc.set(node, 123) == 123
    assert loc.get(node) == 123
    loc.remove(node)
    assert loc.get(node) is None
    # removing again is a no-op
    loc.remove(node)
    assert isinstance(loc.toString(), str)


def test_pointer_variants() -> None:
    e = SimpleNamespace(clientX=1, clientY=2)
    assert s.pointer(e) == [1.0, 2.0]
    assert s.pointer({"clientX": 3, "clientY": 4}) == [3.0, 4.0]
    assert s.pointer({"pageX": 5, "pageY": 6}) == [5.0, 6.0]
    assert s.pointer({}) == [0.0, 0.0]


def test_style_export_style_value_function() -> None:
    node = SimpleNamespace(style={"color": "red"})
    assert style_mod.styleValue(node, "color") == "red"
    assert style_mod.styleValue(None, "color") is None
    assert style_mod.styleValue(SimpleNamespace(style={}), "color") is None
    assert style_mod.styleValue(SimpleNamespace(style="nope"), "color") is None


def test_window_helper_branches(jsdom) -> None:
    doc = jsdom("<div></div>")
    assert s.window(doc).document is doc
    # arbitrary node falls back to global document.defaultView
    assert s.window(doc.body).document is doc
    # when global document is None, window() returns None
    import pyd3js_selection._globals as g

    g.document = None
    assert s.window(SimpleNamespace()) is None


def test_dom_parser_and_selectors_smoke() -> None:
    doc = parse_html(
        "<html><body><svg><g id='x'></g></svg><div class='c'></div></body></html>"
    )
    assert doc.querySelector("#x").namespaceURI == "http://www.w3.org/2000/svg"
    assert doc.querySelector(".c").tagName.lower() == "div"
    assert doc.querySelectorAll("div,svg")  # union selector
    assert doc.querySelector("") is None


def test_dom_style_declaration_branches() -> None:
    sd = StyleDeclaration()
    assert sd.getPropertyValue("color") == ""
    assert sd.getPropertyPriority("color") == ""
    sd.setProperty("color", "red", "important")
    assert sd.getPropertyValue("color") == "red"
    assert sd.getPropertyPriority("color") == "important"
    sd.removeProperty("color")
    assert sd.getPropertyValue("color") == ""


def test_selection_index_branch_smoke(jsdom) -> None:
    doc = jsdom("<div id='a'><span class='x'></span></div><div id='b'></div>")
    a = doc.querySelector("#a")
    doc.querySelector("#b")

    # select string when global document exists
    assert s.select("#a").node() is a

    # selectAll string when global document exists
    assert s.selectAll("div").size() == 2

    # select when no global document
    import pyd3js_selection._globals as g

    g.document = None
    assert s.select("div").node() is None
    assert s.selectAll("div").nodes() == []

    # restore
    g.document = doc

    # filter string branch where node has no parent (forces False path)
    orphan = Element(tagName="DIV")
    assert s.selectAll([orphan]).filter("#nope").nodes() == []

    # selectChildren match branch (non-*)
    assert s.select(a).selectChildren("span").size() == 1
    assert s.select(a).selectChildren("div").size() == 0

    # selectChild callable branch
    assert (
        s.select(a)
        .selectChild(lambda this, d=None, i=0, nodes=None: True)
        .node()
        .tagName.lower()
        == "span"
    )

    # on no-op path and removals
    sel = s.select(a).on(".foo", lambda this, e=None, d=None, nodes=None: None)
    assert sel.node() is a
    s.select(a).on("click.foo", lambda this, e=None, d=None, nodes=None: None, True)
    s.select(a).on("click.foo", None, False)
    s.select(a).on(".foo", None)

    # dispatch params callable branch
    s.select(a).on("bang", lambda this, e, d: None).dispatch(
        "bang", lambda d, i: {"detail": i}
    )

    # join shorthand
    s.select(doc.body).selectAll("p").data([1]).join("p")

    # attr dict-method paths
    seen: dict[str, str | None] = {"v": None}
    node = {
        "getAttribute": lambda name: "ok" if name == "foo" else None,
        "setAttribute": lambda name, value: seen.__setitem__("v", value),
        "removeAttribute": lambda name: seen.__setitem__("v", name),
    }
    assert s.select(node).attr("foo") == "ok"
    s.select(node).attr("foo", "bar")
    assert seen["v"] == "bar"
    s.select(node).attr("foo", None)
    assert seen["v"] == "foo"


def test_creator_document_fallback_branch() -> None:
    import pyd3js_selection._globals as g

    g.document = None
    c = s.creator("h1")
    el = c(None)
    assert isinstance(el, Element)

    # ensure Document.createElementNS uppercases HTML tags
    d = Document()
    p = d.createElementNS("http://www.w3.org/1999/xhtml", "p")
    assert p.tagName == "P"


def test_select_all_non_list_tuple_branch(jsdom) -> None:
    jsdom("<div></div>")
    assert s.selectAll(123).nodes() == [123]


def test_matcher_and_namespace_extra_branches() -> None:
    el = Element(tagName="DIV")
    el.setAttribute("id", "a")
    el.setAttribute("class", "c1 c2")
    assert matcher("#a")(el) is True
    assert matcher(".c2")(el) is True
    assert matcher("div.c1")(el) is True
    assert matcher("span.c1")(el) is False
    assert matcher("span")(el) is False

    assert namespace("xmlns:foo")["space"].endswith("xmlns/")
    assert namespace("nope:bar") == "bar"

    import pyd3js_selection.namespaces as ns_mod

    old = ns_mod.get("xmlns")
    try:
        ns_mod.pop("xmlns", None)
        assert namespace("xmlns:foo") == "xmlns:foo"
    finally:
        if old is not None:
            ns_mod["xmlns"] = old
