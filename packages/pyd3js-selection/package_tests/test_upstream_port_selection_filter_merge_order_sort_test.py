from __future__ import annotations

import pyd3js_selection as s


def _assert_selection(sel: s.Selection, *, groups, parents=None) -> None:
    assert sel._groups == groups
    if parents is not None:
        assert sel._parents == parents


def test_filter_returns_selection(jsdom):
    doc = jsdom("<h1>hello</h1>")
    assert isinstance(s.select(doc.body).filter("body"), s.selection)


def test_filter_string_retains_matching(jsdom):
    doc = jsdom(
        "<h1><span id='one'></span><span id='two'></span></h1>"
        "<h1><span id='three'></span><span id='four'></span></h1>"
    )
    one = doc.querySelector("#one")
    three = doc.querySelector("#three")
    out = s.select(doc).selectAll("span").filter("#one,#three")
    _assert_selection(out, groups=[[one, three]], parents=[doc])


def test_filter_function_retains_true(jsdom):
    doc = jsdom(
        "<h1><span id='one'></span><span id='two'></span></h1>"
        "<h1><span id='three'></span><span id='four'></span></h1>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    three = doc.querySelector("#three")
    four = doc.querySelector("#four")

    def fn(this, d, i, nodes):  # noqa: ANN001
        return i & 1

    out = s.selectAll([one, two, three, four]).filter(fn)
    _assert_selection(out, groups=[[two, four]], parents=[None])


def test_filter_function_passes_data_index_nodes(jsdom):
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

    def keep(this, d, i, nodes):  # noqa: ANN001
        results.append([this, d, i, list(nodes)])
        return True

    (
        s.selectAll([one, two])
        .datum(data_parent)
        .selectAll("child")
        .data(data_children)
        .filter(keep)
    )

    assert results == [
        [three, "child-0-0", 0, [three, four]],
        [four, "child-0-1", 1, [three, four]],
        [five, "child-1-0", 0, [five, None]],
    ]


def test_filter_propagates_parents_identity(jsdom):
    doc = jsdom("<parent><child>1</child></parent><parent><child>2</child></parent>")
    parents = s.select(doc).selectAll("parent")
    parents2 = parents.filter(lambda this, d, i, nodes: True)
    _assert_selection(parents, groups=[doc.querySelectorAll("parent")], parents=[doc])
    _assert_selection(parents2, groups=[doc.querySelectorAll("parent")], parents=[doc])
    assert parents._parents is parents2._parents


def test_filter_nested(jsdom):
    doc = jsdom(
        "<parent id='one'><child><span id='three'></span></child></parent>"
        "<parent id='two'><child><span id='four'></span></child></parent>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    three = doc.querySelector("#three")
    four = doc.querySelector("#four")
    out = s.selectAll([one, two]).selectAll("span").filter("*")
    _assert_selection(out, groups=[[three], [four]], parents=[one, two])


def test_filter_skips_missing_and_does_not_retain_indexes(jsdom):
    doc = jsdom("<h1>hello</h1>")
    h1 = doc.querySelector("h1")
    _assert_selection(
        s.selectAll([None, h1]).filter("*"), groups=[[h1]], parents=[None]
    )


def test_merge_merges_two_selections(jsdom):
    doc = jsdom("<h1 id='one'>one</h1><h1 id='two'>two</h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    selection0 = s.select(doc.body).selectAll("h1")
    selection1 = selection0.select(
        lambda this: this if this.getAttribute("id") == "two" else None
    )
    selection2 = selection0.select(
        lambda this: this if this.getAttribute("id") == "one" else None
    )
    _assert_selection(
        selection1.merge(selection2), groups=[[one, two]], parents=[doc.body]
    )
    _assert_selection(selection1, groups=[[None, two]], parents=[doc.body])
    _assert_selection(selection2, groups=[[one, None]], parents=[doc.body])


def test_order_moves_selected_elements(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([two, one])
    assert sel.order() is sel
    assert one.nextSibling is None
    assert two.nextSibling is one


def test_sort_sorts_and_orders(jsdom):
    doc = jsdom(
        "<h1 id='one' data-value='1'></h1><h1 id='two' data-value='0'></h1><h1 id='three' data-value='2'></h1>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    three = doc.querySelector("#three")

    selection0 = s.selectAll([two, three, one]).datum(
        lambda this, d, i, nodes: int(this.getAttribute("data-value"))
    )
    selection1 = selection0.sort(lambda a, b: a - b)
    _assert_selection(selection0, groups=[[two, three, one]], parents=[None])
    _assert_selection(selection1, groups=[[two, one, three]], parents=[None])
    assert two.nextSibling is one
    assert one.nextSibling is three
    assert three.nextSibling is None
