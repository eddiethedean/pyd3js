from __future__ import annotations

import pyd3js_selection as s


def test_on_registers_and_dispatch_calls_each(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    clicks = {"n": 0}

    def clicked(this, e=None, d=None, nodes=None):  # noqa: ANN001
        clicks["n"] += 1

    sel = s.selectAll([one, two])
    assert sel.on("click", clicked) is sel
    sel.dispatch("click")
    assert clicks["n"] == 2
    sel.dispatch("tick")
    assert clicks["n"] == 2


def test_on_namespaces(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    foo = {"n": 0}
    bar = {"n": 0}

    sel = (
        s.selectAll([one, two])
        .on("click.foo", lambda this, e=None, d=None, nodes=None: foo.__setitem__("n", foo["n"] + 1))
        .on("click.bar", lambda this, e=None, d=None, nodes=None: bar.__setitem__("n", bar["n"] + 1))
    )
    sel.dispatch("click")
    assert foo["n"] == 2
    assert bar["n"] == 2


def test_on_getter_and_removals_and_name_wildcard(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    foo = {"n": 0}
    bar = {"n": 0}

    def fooed(this, e=None, d=None, nodes=None):  # noqa: ANN001
        foo["n"] += 1

    def barred(this, e=None, d=None, nodes=None):  # noqa: ANN001
        bar["n"] += 1

    s2 = s.selectAll([one, two]).on("click.foo", fooed).on("click.bar", barred)
    assert s2.on("click") is None
    assert s2.on("click.foo") is fooed
    assert s2.on("click.bar") is barred
    assert s2.on(".foo") is None

    assert s2.on("click.foo", None) is s2
    assert s2.on("click.foo") is None
    s2.dispatch("click")
    assert foo["n"] == 0
    assert bar["n"] == 2

    assert s2.on(".bar", None) is s2
    assert s2.on("click.bar") is None


def test_on_capture_flag_is_passed(jsdom):
    jsdom("")
    seen = {"capture": None}

    node = {"addEventListener": lambda _t, _l, c: seen.__setitem__("capture", c)}
    s.select(node).on("click.foo", lambda this, e=None, d=None, nodes=None: None, True)
    assert seen["capture"] is True


def test_dispatch_passes_event_type_and_datum(jsdom):
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

    s3 = (
        s.selectAll([one, two])
        .datum(lambda _this, _d, i, _nodes: f"parent-{i}")
        .selectAll("child")
        .data(lambda _d, i, _nodes: [f"child-{i}-0", f"child-{i}-1"])
        .on("foo", lambda this, e, d: results.append([this, e.type, d]))
    )
    assert results == []
    s3.dispatch("foo")
    assert results == [
        [three, "foo", "child-0-0"],
        [four, "foo", "child-0-1"],
        [five, "foo", "child-1-0"],
    ]


def test_on_listener_uses_current_node_datum(jsdom):
    doc = jsdom("")
    results = []
    sel = s.select(doc).on("foo", lambda this, e, d: results.append(d))
    sel.dispatch("foo")
    doc.__dict__["__data__"] = 42
    sel.dispatch("foo")
    assert results == [None, 42]


def test_dispatch_event_params(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    seen = {"e": None}
    out = []

    def bang(this, e, d):  # noqa: ANN001
        seen["e"] = e
        out.extend([this, d])

    sel = s.selectAll([one, two]).datum(lambda _d, i: f"node-{i}").on("bang", bang)
    sel.dispatch("bang", {"bubbles": True, "cancelable": True, "detail": "loud"})
    assert out == [one, "node-0", two, "node-1"]
    assert seen["e"].type == "bang"
    assert seen["e"].bubbles is True
    assert seen["e"].cancelable is True
    assert seen["e"].detail == "loud"

