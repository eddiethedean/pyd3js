from __future__ import annotations

import pytest

import pyd3js_selection as s
from pyd3js_selection.selection.index import EnterNode


def test_data_binds_by_index_and_sets_enter_exit(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div><div id='three'></div>")
    one = doc.body.querySelector("#one")
    two = doc.body.querySelector("#two")
    three = doc.body.querySelector("#three")
    sel = s.select(doc.body).selectAll("div").data(["foo", "bar", "baz"])
    assert one.__data__ == "foo"
    assert two.__data__ == "bar"
    assert three.__data__ == "baz"
    assert sel._groups == [[one, two, three]]
    assert sel._parents == [doc.body]
    assert sel._enter == [[None, None, None]]
    assert sel._exit == [[None, None, None]]


def test_data_accepts_iterable(jsdom):
    jsdom("<div></div><div></div><div></div>")
    sel = s.select(s.document.body).selectAll("div").data(("foo", "bar", "baz"))
    assert sel.data() == ["foo", "bar", "baz"]


def test_data_null_not_allowed(jsdom):
    jsdom("<div></div>")
    with pytest.raises(TypeError):
        s.select(s.document.body).selectAll("div").data(None)


def test_enter_contains_enter_nodes(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    sel = s.select(doc.body).selectAll("div").data(["foo", "bar", "baz"])
    en = sel.enter().node()
    assert isinstance(en, EnterNode)
    assert en._parent is doc.body


def test_exit_contains_unbound_elements(jsdom):
    doc = jsdom("<div id='one'></div><div id='two'></div>")
    sel = s.select(doc.body).selectAll("div").data(["foo"])
    ex = sel.exit()
    assert ex._groups[0][1] is doc.body.querySelector("#two")


def test_data_keyed_join_duplicate_keys_and_ordering(jsdom):
    doc = jsdom("<node id='one'></node><node id='two'></node><node id='three'></node>")
    one = doc.body.querySelector("#one")
    two = doc.body.querySelector("#two")
    three = doc.body.querySelector("#three")

    sel = s.select(doc.body).selectAll("node").data(["one", "four", "three"], lambda this, d, i, nodes: d or this.attributes.get("id"))
    assert sel._groups == [[one, None, three]]
    assert isinstance(sel._enter[0][1], EnterNode)
    assert sel._exit[0][1] is two

    doc = jsdom("<node id='one' name='foo'></node><node id='two' name='foo'></node><node id='three' name='bar'></node>")
    one = doc.body.querySelector("#one")
    two = doc.body.querySelector("#two")
    three = doc.body.querySelector("#three")
    sel = s.select(doc.body).selectAll("node").data(["foo"], lambda this, d, i, nodes: d or this.getAttribute("name"))
    assert sel._groups == [[one]]
    assert sel._exit[0][1] is two and sel._exit[0][2] is three

    sel = s.select(doc.body).selectAll("node").data(["bar"], lambda this, d, i, nodes: d or this.getAttribute("name"))
    assert sel._groups == [[three]]
    assert sel._exit[0][0] is one and sel._exit[0][1] is two


def test_join_name_appends_and_removes(jsdom):
    doc = jsdom("<p>1</p><p>2</p><p>3</p>")
    p = s.select(doc.body).selectAll("p")
    p = p.data([1, 3]).join("p").text(lambda d, i=None, nodes=None: d)  # type: ignore[arg-type]
    assert doc.body.innerHTML == "<p>1</p><p>3</p>"


def test_join_callbacks_update_exit_and_enter(jsdom):
    doc = jsdom("<p>1</p><p>2</p>")
    p = s.select(doc.body).selectAll("p").datum(lambda this, d, i, nodes: this.textContent)

    def k(d, i=None, nodes=None):  # noqa: ANN001
        return d

    p = p.data([1, 3], k).join(
        lambda enter: enter.append("p").attr("class", "enter").text(lambda d, i=None, nodes=None: d),
        lambda update: update.attr("class", "update"),
        lambda exit: exit.attr("class", "exit"),
    )
    assert doc.body.innerHTML == '<p class="update">1</p><p class="exit">2</p><p class="enter">3</p>'


def test_join_reorders_nodes_to_match_data(jsdom):
    doc = jsdom("")
    p = s.select(doc.body).selectAll("p")

    p = p.data([1, 3], lambda d, i=None, nodes=None: d).join(
        lambda enter: enter.append("p").text(lambda d, i=None, nodes=None: d)
    )
    assert doc.body.innerHTML == "<p>1</p><p>3</p>"

    p = p.data([0, 3, 1, 2, 4], lambda d, i=None, nodes=None: d).join(
        lambda enter: enter.append("p").text(lambda d, i=None, nodes=None: d)
    )
    assert doc.body.innerHTML == "<p>0</p><p>3</p><p>1</p><p>2</p><p>4</p>"


def test_join_allows_transition_returns(jsdom):
    doc = jsdom("<p>1</p><p>2</p>")
    p = s.select(doc.body).selectAll("p").datum(lambda this, d, i, nodes: this.textContent)

    def mock_transition(sel: s.Selection):
        class T:
            def selection(self):
                return sel

        return T()

    p = p.data([1, 3], lambda d, i=None, nodes=None: d).join(
        lambda enter: mock_transition(enter.append("p").attr("class", "enter").text(lambda d, i=None, nodes=None: d)),
        lambda update: mock_transition(update.attr("class", "update")),
        lambda exit: mock_transition(exit.attr("class", "exit")),
    )
    assert doc.body.innerHTML == '<p class="update">1</p><p class="exit">2</p><p class="enter">3</p>'

