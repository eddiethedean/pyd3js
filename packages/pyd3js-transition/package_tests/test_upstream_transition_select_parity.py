"""Ports of d3-transition@3.0.1 ``select-test.js`` / ``selectAll-test.js`` group behaviors."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
from pyd3js_selection.selectAll import selectAll
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition.transition.index import Transition


def _with_virtual_time() -> callable:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return step


def test_transition_select_string_derives_child_transition() -> None:
    g.document = parse_html(
        """
        <html>
          <body>
            <div id="one"><child></child></div>
            <div id="two"><child></child></div>
          </body>
        </html>
        """
    )
    _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    c1 = one.firstChild
    c2 = two.firstChild
    assert c1 is not None and c2 is not None
    t1 = selectAll([one, two]).data([1, 2]).transition().delay(lambda d, *_args: d * 10)
    t2 = t1.select("child")
    assert isinstance(t2, Transition)
    assert t2._groups == [[c1, c2]]
    assert t2._parents is t1._parents
    assert t2._name == t1._name
    assert t2._id == t1._id
    assert getattr(c1, "__data__", None) == 1
    assert getattr(c2, "__data__", None) == 2
    assert c1.__transition__[t1._id]["delay"] == 10
    assert c2.__transition__[t1._id]["delay"] == 20


def test_transition_select_function_derives_child_transition() -> None:
    g.document = parse_html(
        """
        <html>
          <body>
            <div id="one"><child></child></div>
            <div id="two"><child></child></div>
          </body>
        </html>
        """
    )
    _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    c1 = one.firstChild
    c2 = two.firstChild
    assert c1 is not None and c2 is not None
    t1 = selectAll([one, two]).data([1, 2]).transition().delay(lambda d, *_args: d * 10)

    def pick(this, *_args):  # noqa: ANN001
        return this.firstChild

    t2 = t1.select(pick)
    assert isinstance(t2, Transition)
    assert t2._groups == [[c1, c2]]
    assert t2._parents is t1._parents
    assert t2._name == t1._name
    assert t2._id == t1._id
