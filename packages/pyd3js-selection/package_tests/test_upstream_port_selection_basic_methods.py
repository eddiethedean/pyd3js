from __future__ import annotations

import pyd3js_selection as d3


def test_empty(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    assert d3.select(doc).empty() is False
    assert d3.select(None).empty() is True
    assert d3.selectAll([]).empty() is True
    assert d3.selectAll([None]).empty() is True


def test_node_skips_missing(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert d3.selectAll([one, two]).node() is one
    assert d3.selectAll([None, one, None, two]).node() is one
    assert d3.select(None).node() is None


def test_nodes_and_size(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert d3.selectAll([one, two]).nodes() == [one, two]
    assert d3.selectAll([None, one, None, two]).nodes() == [one, two]
    assert d3.selectAll([]).size() == 0
    assert d3.selectAll([one]).size() == 1
    assert d3.selectAll([one, two]).size() == 2


def test_each_and_call(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = []
    sel = d3.selectAll([one, two]).datum(lambda d, i: f"node-{i}")

    def f(this, d, i, nodes):
        out.extend([this, d, i, nodes])

    assert sel.each(f) is sel
    assert out == [one, "node-0", 0, [one, two], two, "node-1", 1, [one, two]]

    got = []
    s = d3.select(doc)
    assert s.call(lambda s, a, b: got.extend([s, a, b]), 1, 2) is s
    assert got[1:] == [1, 2]


def test_text_html_property_style_smoke():
    one = type("N", (), {})()
    two = type("N", (), {})()
    one.textContent = ""
    two.textContent = ""
    sel = d3.selectAll([one, two])
    sel.text("bar")
    assert one.textContent == "bar"
    sel.text(None)
    assert one.textContent == ""

    one.innerHTML = ""
    two.innerHTML = ""
    sel.html("x")
    assert one.innerHTML == "x"

    one.foo = 1
    assert d3.select(one).property("foo") == 1
    sel.property("foo", "bar")
    assert one.foo == "bar"
    sel.property("foo", None)
    assert not hasattr(one, "foo")

