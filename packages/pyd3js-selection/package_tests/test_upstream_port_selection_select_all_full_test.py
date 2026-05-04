from __future__ import annotations

import pyd3js_selection as s


def _assert_selection(sel: s.Selection, *, groups, parents=None) -> None:
    assert sel._groups == groups
    if parents is not None:
        assert sel._parents == parents


def test_selection_select_all_string(jsdom):
    doc = jsdom(
        "<h1 id='one'><span></span><span></span></h1><h1 id='two'><span></span><span></span></h1>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).selectAll("span")
    _assert_selection(
        out,
        groups=[one.querySelectorAll("span"), two.querySelectorAll("span")],
        parents=[one, two],
    )


def test_selection_select_all_function_and_args(jsdom):
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

    def fn(this, d, i, nodes):  # noqa: ANN001
        results.append([this, d, i, list(nodes)])
        return [this]

    s.selectAll([one, two]).datum(data_parent).selectAll("child").data(
        data_children
    ).selectAll(fn)
    assert results == [
        [three, "child-0-0", 0, [three, four]],
        [four, "child-0-1", 1, [three, four]],
        [five, "child-1-0", 0, [five, None]],
    ]


def test_selection_select_all_does_not_propagate_data(jsdom):
    doc = jsdom("<parent><child>hello</child></parent>")
    parent = doc.querySelector("parent")
    child = doc.querySelector("child")
    parent.__data__ = 42
    s.select(parent).selectAll("child")
    assert "__data__" not in child.__dict__


def test_selection_select_all_groups_by_parent(jsdom):
    doc = jsdom(
        "<parent id='one'><child id='three'></child></parent><parent id='two'><child id='four'></child></parent>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    three = doc.querySelector("#three")
    four = doc.querySelector("#four")
    _assert_selection(
        s.select(doc).selectAll("parent").selectAll("child"),
        groups=[[three], [four]],
        parents=[one, two],
    )
    _assert_selection(
        s.select(doc).selectAll("child"), groups=[[three, four]], parents=[doc]
    )


def test_selection_select_all_skips_missing(jsdom):
    doc = jsdom("<h1><span>hello</span></h1>")
    h1 = doc.querySelector("h1")
    span = doc.querySelector("span")
    _assert_selection(
        s.selectAll([None, h1]).selectAll("span"), groups=[[span]], parents=[h1]
    )
