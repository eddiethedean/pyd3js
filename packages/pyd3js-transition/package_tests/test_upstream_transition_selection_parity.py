"""Port of d3-transition@3.0.1 ``selection-test.js``."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_selection.selection.index import selection as Selection


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


def test_transition_selection_returns_matching_selection() -> None:
    g.document = parse_html(
        """
        <html>
          <body>
            <h1></h1>
            <h1></h1>
          </body>
        </html>
        """
    )
    _with_virtual_time()
    body = g.document.body
    assert body is not None
    s0 = select(body).selectAll("h1")
    t = s0.transition()
    s1 = t.selection()
    assert isinstance(s1, Selection)
    assert s1._groups is s0._groups
    assert s1._parents is s0._parents
