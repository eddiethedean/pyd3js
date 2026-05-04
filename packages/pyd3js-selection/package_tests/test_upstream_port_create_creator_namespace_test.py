from __future__ import annotations

import pyd3js_selection as s


def test_create_html_element(jsdom):
    jsdom("")
    h1 = s.create("h1")
    assert h1._groups[0][0].namespaceURI == "http://www.w3.org/1999/xhtml"
    assert h1._groups[0][0].tagName == "H1"
    assert h1._parents == [None]


def test_create_svg_element(jsdom):
    jsdom("")
    svg = s.create("svg")
    assert svg._groups[0][0].namespaceURI == "http://www.w3.org/2000/svg"
    assert svg._groups[0][0].tagName == "svg"
    assert svg._parents == [None]


def test_creator_creates_expected_types(jsdom):
    doc = jsdom("<body class='foo'>")
    body = doc.body
    type_ = lambda el: {"namespace": el.namespaceURI, "name": el.tagName}
    assert type_(s.creator("h1")(body)) == {
        "namespace": "http://www.w3.org/1999/xhtml",
        "name": "H1",
    }
    assert type_(s.creator("xhtml:h1")(body)) == {
        "namespace": "http://www.w3.org/1999/xhtml",
        "name": "H1",
    }
    assert type_(s.creator("svg")(body)) == {
        "namespace": "http://www.w3.org/2000/svg",
        "name": "svg",
    }
    assert type_(s.creator("g")(body)) == {
        "namespace": "http://www.w3.org/1999/xhtml",
        "name": "G",
    }


def test_creator_inherits_namespace(jsdom):
    doc = jsdom("<body class='foo'><svg></svg>")
    svg = doc.querySelector("svg")
    assert {"namespace": s.creator("g")(doc.body).namespaceURI, "name": s.creator("g")(doc.body).tagName} == {
        "namespace": "http://www.w3.org/1999/xhtml",
        "name": "G",
    }
    assert {"namespace": s.creator("g")(svg).namespaceURI, "name": s.creator("g")(svg).tagName} == {
        "namespace": "http://www.w3.org/2000/svg",
        "name": "g",
    }


def test_namespaces_value():
    assert s.namespaces == {
        "svg": "http://www.w3.org/2000/svg",
        "xhtml": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
    }


def test_namespace_behavior_and_modifications():
    assert s.namespace("foo") == "foo"
    assert s.namespace("foo:bar") == "bar"

    class X:
        def __str__(self):
            return "foo"

    assert s.namespace(X()) == "foo"

    class Y:
        def __str__(self):
            return "svg"

    assert s.namespace(Y()) == {"space": "http://www.w3.org/2000/svg", "local": "svg"}

    assert s.namespace("svg") == {"space": "http://www.w3.org/2000/svg", "local": "svg"}
    assert s.namespace("xhtml") == {"space": "http://www.w3.org/1999/xhtml", "local": "xhtml"}
    assert s.namespace("xlink") == {"space": "http://www.w3.org/1999/xlink", "local": "xlink"}
    assert s.namespace("xml") == {"space": "http://www.w3.org/XML/1998/namespace", "local": "xml"}
    assert s.namespace("svg:g") == {"space": "http://www.w3.org/2000/svg", "local": "g"}
    assert s.namespace("xhtml:b") == {"space": "http://www.w3.org/1999/xhtml", "local": "b"}
    assert s.namespace("xlink:href") == {"space": "http://www.w3.org/1999/xlink", "local": "href"}
    assert s.namespace("xml:lang") == {"space": "http://www.w3.org/XML/1998/namespace", "local": "lang"}

    assert s.namespace("xmlns:xlink") == {
        "space": "http://www.w3.org/2000/xmlns/",
        "local": "xmlns:xlink",
    }

    s.namespaces["d3js"] = "https://d3js.org/2016/namespace"
    assert s.namespace("d3js:pie") == {"space": "https://d3js.org/2016/namespace", "local": "pie"}
    del s.namespaces["d3js"]
    assert s.namespace("d3js:pie") == "pie"

