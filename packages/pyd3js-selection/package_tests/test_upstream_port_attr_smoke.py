from __future__ import annotations

import pyd3js_selection as s


def test_attr_get_set_remove(jsdom):
    doc = jsdom("<h1 class='c1 c2'>hello</h1><h1 class='c3'></h1>")
    assert s.select(doc).select("h1").attr("class") == "c1 c2"

    one = doc.querySelector("#one")


def test_attr_set_and_remove_on_elements(jsdom):
    doc = jsdom("<h1 id='one' foo='bar'></h1><h1 id='two' foo='bar'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([one, two])
    sel.attr("foo", "baz")
    assert one.getAttribute("foo") == "baz"
    assert two.getAttribute("foo") == "baz"
    sel.attr("foo", None)
    assert one.hasAttribute("foo") is False
    assert two.hasAttribute("foo") is False

