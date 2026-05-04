"""Ports of d3-transition@3.0.1 ``remove-test.js`` (virtual timer)."""

from __future__ import annotations

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html
from pyd3js_selection.select import select
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)


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


def test_transition_remove_detaches_element_on_end() -> None:
    g.document = parse_html(
        """
        <html>
          <body><div id="inner"></div></body>
        </html>
        """
    )
    step = _with_virtual_time()
    root = g.document.documentElement
    body = g.document.body
    assert body is not None
    started = {"ok": False}
    ended = {"ok": False}

    def started_cb(*_args) -> None:
        started["ok"] = True
        assert body.parentNode is root

    def ended_cb(*_args) -> None:
        ended["ok"] = True
        assert body.parentNode is None

    s = select(body)
    t = s.transition().remove().on("start", started_cb).on("end", ended_cb)
    end = t.end()
    step(0)
    assert started["ok"] is True
    assert body.parentNode is root
    step(300)
    assert ended["ok"] is True
    assert body.parentNode is None
    end.result(timeout=5.0)


def test_transition_remove_listener_can_be_invoked_manually() -> None:
    g.document = parse_html(
        """
        <html>
          <body><div id="inner"></div></body>
        </html>
        """
    )
    step = _with_virtual_time()
    root = g.document.documentElement
    body = g.document.body
    assert body is not None

    def started_cb(*_args) -> None:
        assert body.parentNode is root

    def ended_cb(*_args) -> None:
        assert body.parentNode is root

    s = select(body)
    t = s.transition().remove().on("start", started_cb).on("end", ended_cb)
    end = t.end()
    rm = t.on("end.remove")
    assert rm is not None
    rm(body)
    assert body.parentNode is None
    t.on("end.remove", None)
    root.appendChild(body)
    step(0)
    step(300)
    end.result(timeout=5.0)
