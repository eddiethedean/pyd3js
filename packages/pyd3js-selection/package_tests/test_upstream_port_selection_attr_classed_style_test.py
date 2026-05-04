from __future__ import annotations

import pyd3js_selection as s


def test_attr_get_coerces_and_namespaces(jsdom):
    doc = jsdom("<h1 class='c1 c2'>hello</h1><h1 class='c3'></h1>")
    assert s.select(doc).select("h1").attr("class") == "c1 c2"
    assert s.selectAll([None, doc]).select("h1").attr("class") == "c1 c2"

    class X:
        def __str__(self) -> str:
            return "class"

    assert s.select(doc).select("h1").attr(X()) == "c1 c2"

    sel = s.select(
        {
            "getAttribute": lambda name: "bar" if name == "foo" else None,
            "getAttributeNS": lambda url, name: (
                "svg:bar"
                if url == "http://www.w3.org/2000/svg" and name == "foo"
                else None
            ),
        }
    )
    assert sel.attr("foo") == "bar"
    assert sel.attr("svg:foo") == "svg:bar"


def test_attr_set_remove_and_callback_args(jsdom):
    doc = jsdom("<h1 id='one' class='c1 c2'>hello</h1><h1 id='two' class='c3'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([one, two])
    assert sel.attr("foo", "bar") is sel
    assert one.getAttribute("foo") == "bar"
    assert two.getAttribute("foo") == "bar"
    assert sel.attr("foo", None) is sel
    assert one.hasAttribute("foo") is False
    assert two.hasAttribute("foo") is False

    sel = s.selectAll([one, two])
    assert (
        sel.attr("foo", lambda _this, _d, i, _nodes: f"bar-{i}" if i else None) is sel
    )
    assert one.hasAttribute("foo") is False
    assert two.getAttribute("foo") == "bar-1"

    doc = jsdom(
        "<parent id='one'><child id='three'></child><child id='four'></child></parent>"
        "<parent id='two'><child id='five'></child></parent>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    three = doc.querySelector("#three")
    four = doc.querySelector("#four")
    five = doc.querySelector("#five")
    results = []

    s.selectAll([one, two]).datum(lambda _this, _d, i, _nodes: f"parent-{i}").selectAll(
        "child"
    ).data(lambda _d, i, _nodes: [f"child-{i}-0", f"child-{i}-1"]).attr(
        "foo", lambda this, d, i, nodes: results.append([this, d, i, list(nodes)])
    )

    assert results == [
        [three, "child-0-0", 0, [three, four]],
        [four, "child-0-1", 1, [three, four]],
        [five, "child-1-0", 0, [five, None]],
    ]


def test_classed_get_and_set(jsdom):
    doc = jsdom("<h1 class='c1 c2'>hello</h1><h1 class='c3'></h1>")
    h1 = s.select(doc).select("h1")
    assert h1.classed("") is True
    assert h1.classed("c1") is True
    assert h1.classed("c2") is True
    assert h1.classed("c3") is False
    assert h1.classed("c1 c2") is True
    assert h1.classed("c2 c1") is True
    assert h1.classed("c1 c3") is False

    b = s.select(doc.body)
    assert b.classed("c1") is False
    assert b.attr("class") is None
    assert b.classed("c1", True) is b
    assert b.attr("class") == "c1"
    assert b.classed("c1 c2", True) is b
    assert b.attr("class") == "c1 c2"
    assert b.classed("c1", False) is b
    assert b.attr("class") == "c2"
    assert b.classed("c1 c2", False) is b
    assert b.attr("class") == ""


def test_style_get_set_remove(jsdom):
    node = {
        "style": {"getPropertyValue": lambda name: "red" if name == "color" else ""},
    }
    assert s.select(node).style("color") == "red"

    styles = {
        "getPropertyValue": lambda name: "rgb(255, 0, 0)" if name == "color" else ""
    }
    node = {
        "style": {"getPropertyValue": lambda _name=None: ""},
        "ownerDocument": {
            "defaultView": {"getComputedStyle": lambda n: styles if n is node else None}
        },
    }
    assert s.select(node).style("color") == "rgb(255, 0, 0)"

    doc = jsdom("<h1 id='one' class='c1 c2'>hello</h1><h1 id='two' class='c3'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([one, two])
    assert sel.style("color", "red") is sel
    assert one.style.getPropertyValue("color") == "red"
    assert two.style.getPropertyValue("color") == "red"
    assert sel.style("color", None) is sel
    assert one.style.getPropertyValue("color") == ""
    assert two.style.getPropertyValue("color") == ""
