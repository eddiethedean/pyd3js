from __future__ import annotations

import pyd3js_selection as s


def test_remove_removes_selected_elements_from_parent(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([two, one])
    assert sel.remove() is sel
    assert one.parentNode is None
    assert two.parentNode is None


def test_remove_skips_already_detached(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([two, one])
    one.parentNode.removeChild(one)
    assert sel.remove() is sel
    assert one.parentNode is None
    assert two.parentNode is None


def test_remove_skips_missing_elements(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    sel = s.selectAll([None, one])
    assert sel.remove() is sel
    assert one.parentNode is None
    assert two.parentNode is doc.body


def test_select_children_remove_removes_all_children(jsdom):
    doc = jsdom(
        "<div><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span>"
        "<span>5</span><span>6</span><span>7</span><span>8</span><span>9</span></div>"
    )
    p = doc.querySelector("div")
    sel = s.select(p).selectChildren()
    assert sel.size() == 10
    assert sel.remove() is sel
    assert s.select(p).selectChildren().size() == 0
