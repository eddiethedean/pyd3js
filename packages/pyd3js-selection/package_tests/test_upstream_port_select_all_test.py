from __future__ import annotations

import pyd3js_selection as s


def _assert_selection(sel: s.Selection, *, groups, parents=None) -> None:
    assert sel._groups == groups
    if parents is not None:
        assert sel._parents == parents


def test_select_all_returns_instanceof_selection(jsdom):
    doc = jsdom("<h1>hello</h1>")
    assert isinstance(s.selectAll([doc]), s.Selection)


def test_select_all_accepts_iterable(jsdom):
    doc = jsdom("<h1>hello</h1>")
    out = s.selectAll((doc,))
    assert out.nodes() == [doc]


def test_select_all_string_selects_all_in_order(jsdom):
    doc = jsdom("<h1 id='one'>foo</h1><h1 id='two'>bar</h1>")
    out = s.selectAll("h1")
    _assert_selection(out, groups=[doc.querySelectorAll("h1")], parents=[doc.documentElement])


def test_select_all_node_list_selects_all(jsdom):
    doc = jsdom("<h1>hello</h1><h2>world</h2>")
    nl = doc.querySelectorAll("h1,h2")
    out = s.selectAll(nl)
    _assert_selection(out, groups=[nl])


def test_select_all_array_selects_array(jsdom):
    doc = jsdom("<h1>hello</h1><h2>world</h2>")
    h1 = doc.querySelector("h1")
    h2 = doc.querySelector("h2")
    out = s.selectAll([h1, h2])
    _assert_selection(out, groups=[[h1, h2]])


def test_select_all_empty_array(jsdom):
    jsdom("")
    out = s.selectAll([])
    _assert_selection(out, groups=[[]])


def test_select_all_null_selects_empty_array(jsdom):
    jsdom("")
    _assert_selection(s.selectAll(), groups=[[]])
    _assert_selection(s.selectAll(None), groups=[[]])


def test_select_all_null_new_empty_each_time(jsdom):
    jsdom("")
    one = s.selectAll()._groups[0]
    two = s.selectAll()._groups[0]
    assert one is not two
    one.append("one")
    assert s.selectAll()._groups[0] == []


def test_select_all_array_can_contain_null(jsdom):
    doc = jsdom("<h1>hello</h1><h2>world</h2>")
    h1 = doc.querySelector("h1")
    out = s.selectAll([None, h1, None])
    _assert_selection(out, groups=[[None, h1, None]])


def test_select_all_array_can_contain_arbitrary_objects(jsdom):
    jsdom("")
    obj = object()
    out = s.selectAll([obj])
    _assert_selection(out, groups=[[obj]])

