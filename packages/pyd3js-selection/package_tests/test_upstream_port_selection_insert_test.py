from __future__ import annotations

import pyd3js_selection as s


def _assert_selection(sel: s.Selection, *, groups, parents=None) -> None:
    assert sel._groups == groups
    if parents is not None:
        assert sel._parents == parents


def test_insert_name_inserts_before_selector(jsdom):
    doc = jsdom(
        "<div id='one'><span class='before'></span></div><div id='two'><span class='before'></span></div>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    out = s.selectAll([one, two]).insert("span", ".before")
    three = one.querySelector("span:first-child")
    four = two.querySelector("span:first-child")
    _assert_selection(out, groups=[[three, four]], parents=[None])


def test_insert_function_function_inserts_before_first_child(jsdom):
    doc = jsdom(
        "<div id='one'><span class='before'></span></div><div id='two'><span class='before'></span></div>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    def make(this, d, i, nodes):  # noqa: ANN001
        return doc.createElement("SPAN")

    def before(this, d, i, nodes):  # noqa: ANN001
        return this.firstChild

    out = s.selectAll([one, two]).insert(make, before)
    three = one.querySelector("span:first-child")
    four = two.querySelector("span:first-child")
    _assert_selection(out, groups=[[three, four]], parents=[None])


def test_insert_function_function_appends_when_before_returns_null(jsdom):
    doc = jsdom(
        "<div id='one'><span class='before'></span></div><div id='two'><span class='before'></span></div>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    def make(this, d, i, nodes):  # noqa: ANN001
        return doc.createElement("SPAN")

    def before(this, d, i, nodes):  # noqa: ANN001
        return None

    out = s.selectAll([one, two]).insert(make, before)
    three = one.querySelector("span:last-child")
    four = two.querySelector("span:last-child")
    _assert_selection(out, groups=[[three, four]], parents=[None])


def test_insert_name_selector_function_receives_data_index_group(jsdom):
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

    def before(this, d, i, nodes):  # noqa: ANN001
        results.append([this, d, i, list(nodes)])
        return None

    (
        s.selectAll([one, two])
        .datum(data_parent)
        .selectAll("child")
        .data(data_children)
        .insert("span", before)
    )

    assert results == [
        [three, "child-0-0", 0, [three, four]],
        [four, "child-0-1", 1, [three, four]],
        [five, "child-1-0", 0, [five, None]],
    ]
