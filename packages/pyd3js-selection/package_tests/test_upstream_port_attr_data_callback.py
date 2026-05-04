from __future__ import annotations

import pyd3js_selection as s


def test_attr_function_callback_receives_expected_args_after_data_join(jsdom):
    doc = jsdom(
        "<h1 id='one'><h2 id='three'></h2><h2 id='four'></h2></h1>"
        "<h1 id='two'><h2 id='five'></h2></h1>"
    )
    one = doc.querySelector("#one")
    two = doc.querySelector("#two")

    three = doc.querySelector("#three")
    four = doc.querySelector("#four")
    five = doc.querySelector("#five")

    seen: list[tuple[object, object, int, list[object | None]]] = []

    def data_fn(d, i, nodes):
        # one has datum "parent0", two has "parent1"
        # return two data items for each parent
        return [f"{d}-child0", f"{d}-child1"]

    def attr_fn(this, d, i, nodes):
        # emulate d3's callback signature from our Selection.each plumbing
        seen.append((this, d, i, list(nodes)))
        return None

    (
        s.selectAll([one, two])
        .datum(lambda _d, i: f"parent{i}")
        .selectAll("h2")
        .data(data_fn)
        .attr("data-x", attr_fn)
    )

    # Update selection should contain existing nodes in order; missing nodes are None holes.
    assert seen == [
        (three, "parent0-child0", 0, [three, four]),
        (four, "parent0-child1", 1, [three, four]),
        (five, "parent1-child0", 0, [five, None]),
    ]

