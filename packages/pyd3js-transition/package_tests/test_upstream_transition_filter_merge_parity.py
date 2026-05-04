"""Ports of d3-transition@3.0.1 ``filter-test.js`` and ``merge-test.js``."""

from __future__ import annotations

import pytest

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


def _two_div_document() -> None:
    g.document = parse_html(
        """
        <html>
          <body>
            <div id="one"></div>
            <div id="two"></div>
          </body>
        </html>
        """
    )


def test_transition_filter_selector_retains_matching_elements() -> None:
    _two_div_document()
    _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = selectAll([one, two]).data([1, 2]).transition().delay(lambda d, *_args: d * 10)
    t2 = t1.filter("#two")
    assert isinstance(t2, Transition)
    assert t2._groups == [[two]]
    assert t2._parents is t1._parents
    assert t2._name == t1._name
    assert t2._id == t1._id


def test_transition_filter_function_retains_matching_elements() -> None:
    _two_div_document()
    _with_virtual_time()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = selectAll([one, two]).data([1, 2]).transition().delay(lambda d, *_args: d * 10)
    t2 = t1.filter(lambda this, *_args: this is two)
    assert isinstance(t2, Transition)
    assert t2._groups == [[two]]
    assert t2._parents is t1._parents
    assert t2._name == t1._name
    assert t2._id == t1._id


def test_transition_merge_combines_null_slots_with_same_id() -> None:
    _two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    root = g.document.documentElement
    t0 = select(root).transition()
    t1 = selectAll([None, two]).transition(t0)
    t2 = selectAll([one, None]).transition(t0)
    t3 = t1.merge(t2)
    assert isinstance(t3, Transition)
    assert t3._groups == [[one, two]]
    assert t3._parents is t1._parents
    assert t3._name == t1._name
    assert t3._id == t1._id


def test_transition_merge_throws_if_other_has_different_id() -> None:
    _two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = selectAll([None, two]).transition()
    t2 = selectAll([one, None]).transition()
    with pytest.raises(RuntimeError):
        t1.merge(t2)
