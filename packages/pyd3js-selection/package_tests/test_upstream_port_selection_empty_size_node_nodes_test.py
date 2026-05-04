from __future__ import annotations

import pyd3js_selection as s


def test_empty_false_if_not_empty(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    assert s.select(doc).empty() is False


def test_empty_true_if_empty(jsdom):
    jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    assert s.select(None).empty() is True
    assert s.selectAll([]).empty() is True
    assert s.selectAll([None]).empty() is True


def test_size_counts_and_skips_missing(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert s.selectAll([]).size() == 0
    assert s.selectAll([one]).size() == 1
    assert s.selectAll([one, two]).size() == 2
    assert s.selectAll([None, one, None, two]).size() == 2


def test_node_first_and_skips_missing_and_empty_groups(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert s.selectAll([one, two]).node() is one
    assert s.selectAll([None, one, None, two]).node() is one

    def fn(this, d=None, i=0, nodes=None):  # noqa: ANN001
        return [this] if i else []

    assert s.selectAll([one, two]).selectAll(fn).node() is two
    assert s.select(None).node() is None
    assert s.selectAll([]).node() is None
    assert s.selectAll([None, None]).node() is None


def test_nodes_merges_groups_and_skips_missing(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert s.selectAll([one, two]).nodes() == [one, two]

    def fn(this, d=None, i=0, nodes=None):  # noqa: ANN001
        return [this]

    assert s.selectAll([one, two]).selectAll(fn).nodes() == [one, two]
    assert s.selectAll([None, one, None, two]).nodes() == [one, two]
