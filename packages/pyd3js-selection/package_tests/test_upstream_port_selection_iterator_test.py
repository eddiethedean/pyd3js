from __future__ import annotations

import pyd3js_selection as s


def test_selection_iterable_over_selected_nodes(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert list(s.selectAll([one, two])) == [one, two]


def test_selection_iteration_merges_nodes_from_all_groups(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    def fn(this):  # noqa: ANN001
        return [this]

    assert list(s.selectAll([one, two]).selectAll(fn)) == [one, two]


def test_selection_iteration_skips_missing_elements(jsdom):
    doc = jsdom("<h1 id='one'></h1><h1 id='two'></h1>")
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")
    assert list(s.selectAll([None, one, None, two])) == [one, two]
