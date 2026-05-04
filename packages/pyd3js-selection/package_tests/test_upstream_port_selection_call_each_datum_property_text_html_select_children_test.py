from __future__ import annotations

import pyd3js_selection as s


def _assert_selection(sel: s.Selection, *, groups, parents=None) -> None:
    assert sel._groups == groups
    if parents is not None:
        assert sel._parents == parents


def test_call_calls_function_and_passes_selection(jsdom):
    jsdom("")
    seen = {}
    sel = s.select(s.document)

    def fn(x):  # noqa: ANN001
        seen["x"] = x

    assert sel.call(fn) is sel
    assert seen["x"] is sel


def test_call_passes_additional_args(jsdom):
    jsdom("")
    out = []
    foo = object()
    bar = object()
    sel = s.select(s.document)

    def fn(x, a, b):  # noqa: ANN001
        out.extend([x, a, b])

    assert sel.call(fn, foo, bar) is sel
    assert out == [sel, foo, bar]


def test_each_calls_for_each_selected_element(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    result = []
    sel = s.selectAll([one, two]).datum(lambda _this, _d, i, _nodes: f"node-{i}")

    def fn(this, d, i, nodes):  # noqa: ANN001
        result.extend([this, d, i, list(nodes)])

    assert sel.each(fn) is sel
    assert result == [one, "node-0", 0, [one, two], two, "node-1", 1, [one, two]]


def test_each_skips_missing(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    result = []
    sel = s.selectAll([None, one, None, two]).datum(
        lambda _this, _d, i, _nodes: f"node-{i}"
    )

    def fn(this, d, i, nodes):  # noqa: ANN001
        result.extend([this, d, i, list(nodes)])

    assert sel.each(fn) is sel
    assert result == [
        one,
        "node-1",
        1,
        [None, one, None, two],
        two,
        "node-3",
        3,
        [None, one, None, two],
    ]


def test_datum_get_set_clear_and_fn(jsdom):
    jsdom("")
    node = {"__data__": "hello"}
    assert s.select(node).datum() == "hello"
    assert s.selectAll([None, node]).datum() == "hello"

    one = {"__data__": ""}
    two = {"__data__": ""}
    sel = s.selectAll([one, two])
    assert sel.datum("bar") is sel
    assert one["__data__"] == "bar" and two["__data__"] == "bar"

    sel = s.selectAll([one, two])
    assert sel.datum(None) is sel
    assert "__data__" not in one and "__data__" not in two

    one = {"__data__": "bar"}
    two = {"__data__": "bar"}
    sel = s.selectAll([one, two])
    assert sel.datum(lambda d, i: "baz" if i else None) is sel
    assert "__data__" not in one
    assert two["__data__"] == "baz"


def test_property_text_html_basic(jsdom):
    jsdom("")
    node = {"foo": 42, "textContent": "hello", "innerHTML": "hello"}
    assert s.select(node).property("foo") == 42
    assert s.select(node).text() == "hello"
    assert s.select(node).html() == "hello"


def test_select_propagates_data(jsdom):
    doc = jsdom("<parent><child>hello</child></parent>")
    parent = doc.querySelector("parent")
    child = doc.querySelector("child")
    parent.__data__ = 0
    child.__data__ = 42
    s.select(parent).select("child")
    assert child.__data__ == 0


def test_select_child_and_select_children(jsdom):
    doc = jsdom("<h1><span>hello</span>, <span>world<span>!</span></span></h1>")
    sel = s.select(doc).select("h1")
    assert isinstance(
        sel.selectChild(lambda this, d=None, i=0, nodes=None: True), s.selection
    )
    assert sel.selectChild("span").text() == "hello"
    assert sel.selectChildren().size() == 2
    assert sel.selectChildren("span").size() == 2
    assert sel.selectChildren("div").size() == 0
