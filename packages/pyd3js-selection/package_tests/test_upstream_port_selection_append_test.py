from __future__ import annotations

import pyd3js_selection as s


def _assert_selection(sel: s.Selection, *, groups, parents=None) -> None:
    assert sel._groups == groups
    if parents is not None:
        assert sel._parents == parents


def test_append_returns_selection(jsdom):
    jsdom("")
    assert isinstance(s.select(s.document.body).append("h1"), s.selection)


def test_append_name_appends_as_last_child(jsdom):
    doc = jsdom("<div id='one'><span class='before'></span></div><div id='two'><span class='before'></span></div>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).append("span")
    three = one.querySelector("span:last-child")
    four = two.querySelector("span:last-child")
    _assert_selection(out, groups=[[three, four]])


def test_append_name_observes_explicit_namespace(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).append("svg:g")
    three = one.querySelector("g")
    four = two.querySelector("g")
    assert three.namespaceURI == "http://www.w3.org/2000/svg"
    assert four.namespaceURI == "http://www.w3.org/2000/svg"
    _assert_selection(out, groups=[[three, four]])


def test_append_uses_create_element_when_implied_namespace_same_as_document(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    pass_count = 0
    create_element = doc.createElement

    def patched(name):  # noqa: ANN001
        nonlocal pass_count
        pass_count += 1
        return create_element(name)

    doc.createElement = patched  # type: ignore[assignment]
    out = s.selectAll([one, two]).append("P")
    three = one.querySelector("p")
    four = two.querySelector("p")
    assert pass_count == 2
    _assert_selection(out, groups=[[three, four]])


def test_append_name_observes_implicit_namespace(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).append("svg")
    three = one.querySelector("svg")
    four = two.querySelector("svg")
    assert three.namespaceURI == "http://www.w3.org/2000/svg"
    assert four.namespaceURI == "http://www.w3.org/2000/svg"
    _assert_selection(out, groups=[[three, four]])


def test_append_name_observes_inherited_namespace(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).append("svg").append("g")
    three = one.querySelector("g")
    four = two.querySelector("g")
    assert three.namespaceURI == "http://www.w3.org/2000/svg"
    assert four.namespaceURI == "http://www.w3.org/2000/svg"
    _assert_selection(out, groups=[[three, four]])


def test_append_custom_namespace(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    try:
        s.namespaces["d3js"] = "https://d3js.org/2016/namespace"
        one = doc.querySelector("#one")
        two = doc.querySelector("#two")
        out = s.selectAll([one, two]).append("d3js")
        three = one.querySelector("d3js")
        four = two.querySelector("d3js")
        assert three.namespaceURI == "https://d3js.org/2016/namespace"
        assert four.namespaceURI == "https://d3js.org/2016/namespace"
        _assert_selection(out, groups=[[three, four]])
    finally:
        s.namespaces.pop("d3js", None)


def test_append_function_appends_returned_element(jsdom):
    doc = jsdom("<div id='one'><span class='before'></span></div><div id='two'><span class='before'></span></div>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    def make(this, d, i, nodes):  # noqa: ANN001
        return doc.createElement("SPAN")

    out = s.selectAll([one, two]).append(make)
    three = one.querySelector("span:last-child")
    four = two.querySelector("span:last-child")
    _assert_selection(out, groups=[[three, four]])


def test_append_function_passes_data_index_group(jsdom):
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

    def data_parent(_d, i):
        return f"parent-{i}"

    def data_children(_d, i, _nodes):
        return [f"child-{i}-0", f"child-{i}-1"]

    def append_fn(this, d, i, nodes):  # noqa: ANN001
        results.append([this, d, i, list(nodes)])
        return doc.createElement("SPAN")

    (
        s.selectAll([one, two])
        .datum(data_parent)
        .selectAll("child")
        .data(data_children)
        .append(append_fn)
    )

    assert results == [
        [three, "child-0-0", 0, [three, four]],
        [four, "child-0-1", 1, [three, four]],
        [five, "child-1-0", 0, [five, None]],
    ]


def test_append_propagates_data_if_defined_on_originating_element(jsdom):
    doc = jsdom("<parent><child>hello</child></parent>")
    parent = doc.querySelector("parent")
    parent.__data__ = 0
    assert s.select(parent).append("child").datum() == 0


def test_append_does_not_propagate_data_if_not_defined_on_originating_element(jsdom):
    doc = jsdom("<parent><child>hello</child></parent>")
    parent = doc.querySelector("parent")
    child = doc.querySelector("child")
    child.__data__ = 42

    def fn(this, d, i, nodes):  # noqa: ANN001
        return child

    s.select(parent).append(fn)
    assert child.__data__ == 42


def test_append_propagates_parents_from_originating_selection(jsdom):
    doc = jsdom("<parent></parent><parent></parent>")
    parents = s.select(doc).selectAll("parent")
    childs = parents.append("child")
    _assert_selection(parents, groups=[doc.querySelectorAll("parent")], parents=[doc])
    _assert_selection(childs, groups=[doc.querySelectorAll("child")], parents=[doc])
    assert parents._parents is childs._parents


def test_append_can_select_elements_when_originating_selection_nested(jsdom):
    doc = jsdom("<parent id='one'><child></child></parent><parent id='two'><child></child></parent>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).selectAll("child").append("span")
    three = one.querySelector("span")
    four = two.querySelector("span")
    _assert_selection(out, groups=[[three], [four]], parents=[one, two])


def test_append_skips_missing_originating_elements(jsdom):
    doc = jsdom("<h1></h1>")
    h1 = doc.querySelector("h1")
    out = s.selectAll([None, h1]).append("span")
    span = h1.querySelector("span")
    _assert_selection(out, groups=[[None, span]])

