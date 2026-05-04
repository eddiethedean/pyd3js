from __future__ import annotations

import pyd3js_selection as s


def test_matcher(jsdom):
    doc = jsdom("<body class='foo'>")
    assert s.matcher("body")(doc.body) is True
    assert s.matcher(".foo")(doc.body) is True
    assert s.matcher("body.foo")(doc.body) is True
    assert s.matcher("h1")(doc.body) is False
    assert s.matcher("body.bar")(doc.body) is False


def test_selector(jsdom):
    doc = jsdom("<body class='foo'>")
    root = doc.documentElement
    assert s.selector("body")(root) == doc.body
    assert s.selector(".foo")(root) == doc.body
    assert s.selector("body.foo")(root) == doc.body
    assert s.selector("h1")(root) is None
    assert s.selector("body.bar")(root) is None

    assert s.selector()(root) is None
    assert s.selector(None)(root) is None


def test_selector_all(jsdom):
    doc = jsdom("<body class='foo'><div class='foo'>")
    root = doc.documentElement
    body = doc.body
    div = doc.querySelector("div")

    assert s.selectorAll("body")(root) == [body]
    assert s.selectorAll(".foo")(root) == [body, div]
    assert s.selectorAll("div.foo")(root) == [div]
    assert s.selectorAll("div")(root) == [div]
    assert s.selectorAll("div,body")(root) == [body, div]
    assert s.selectorAll("h1")(root) == []
    assert s.selectorAll("body.bar")(root) == []

    assert s.selectorAll()(root) == []
    assert s.selectorAll(None)(root) == []

    one = s.selectorAll()()
    two = s.selectorAll()()
    assert one is not two
    one.append("one")
    assert s.selectorAll()() == []


def test_pointer_and_pointers(jsdom):
    doc = jsdom("<div></div>")
    target = doc.querySelector("div")

    def mousemove(x, y, target_=doc.body):
        return {
            "pageX": x,
            "pageY": y,
            "clientX": x,
            "clientY": y,
            "type": "mousemove",
            "target": target_,
            "currentTarget": target_,
        }

    def touch(x, y):
        return {"pageX": x, "pageY": y, "clientX": x, "clientY": y}

    def touchmove(x, y, target_=doc.body):
        return {
            "type": "touchmove",
            "target": target_,
            "currentTarget": target_,
            "touches": [touch(x, y)],
        }

    assert s.pointer(mousemove(10, 20)) == [10, 20]
    assert s.pointer(mousemove(10, 20, target), target) == [10, 20]
    assert s.pointer(touch(10, 20), target) == [10, 20]

    assert s.pointers(mousemove(10, 20)) == [[10, 20]]
    assert s.pointers(mousemove(10, 20, target)) == [[10, 20]]
    assert s.pointers(touchmove(10, 20)) == [[10, 20]]
    assert s.pointers(touchmove(10, 20, target)) == [[10, 20]]
    assert s.pointers([touch(10, 20)]) == [[10, 20]]


def test_window(jsdom):
    doc = jsdom("<body></body>")
    assert s.window(doc.body) == doc.defaultView
    assert s.window(doc) == doc.defaultView
    assert s.window(doc.defaultView) == doc.defaultView
