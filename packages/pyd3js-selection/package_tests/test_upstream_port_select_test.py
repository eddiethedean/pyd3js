from __future__ import annotations

import pyd3js_selection as s


def test_select_returns_instanceof_selection(jsdom):
    doc = jsdom("<h1>hello</h1>")
    assert isinstance(s.select(doc), s.Selection)


def test_select_string_selects_first(jsdom):
    doc = jsdom("<h1 id='one'>foo</h1><h1 id='two'>bar</h1>")
    sel = s.select("h1")
    assert sel._groups[0][0] == doc.querySelector("h1")


def test_select_element(jsdom):
    doc = jsdom("<h1>hello</h1>")
    assert s.select(doc.body)._groups[0][0] == doc.body
    assert s.select(doc.documentElement)._groups[0][0] == doc.documentElement


def test_select_window_document(jsdom):
    doc = jsdom("<h1>hello</h1>")
    assert s.select(doc.defaultView)._groups[0][0] == doc.defaultView
    assert s.select(doc)._groups[0][0] == doc


def test_select_null_and_undefined(jsdom):
    jsdom("<h1>hello</h1>")
    assert s.select(None)._groups[0][0] is None


def test_select_object():
    obj = {}
    assert s.select(obj)._groups[0][0] is obj
