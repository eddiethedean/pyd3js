"""Transition vs selection context, all orientations, enter/exit edge cases."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from pyd3js_axis import axisBottom, axisLeft, axisRight, axisTop
from pyd3js_axis._selection import create, select_node
from pyd3js_axis._svg import Element, outer_html
from pyd3js_axis._transition import Transition


class MockLinear:
    """Minimal `d3.scaleLinear()`-ish scale for axis rendering tests."""

    def __init__(self) -> None:
        self._domain = (0.0, 1.0)
        self._range = (0.0, 1.0)

    def __call__(self, x: object) -> float:
        d0, d1 = self._domain
        r0, r1 = self._range
        if d1 == d0:
            return r0
        t = (float(x) - d0) / (d1 - d0)
        return r0 + t * (r1 - r0)

    def domain(self, d: object | None = None) -> object:
        if d is None:
            return self._domain
        self._domain = (float(d[0]), float(d[1]))  # type: ignore[index]
        return self

    def range(self, r: object | None = None) -> object:
        if r is None:
            return self._range
        self._range = (float(r[0]), float(r[1]))  # type: ignore[index]
        return self

    def ticks(self, *args: object) -> list[float]:
        n = 10
        if args and isinstance(args[0], (int, float)):
            n = int(args[0])
        d0, d1 = self._domain
        if n <= 0:
            return []
        if n == 1:
            return [d0]
        step = (d1 - d0) / (n - 1)
        return [d0 + i * step for i in range(n)]

    def tickFormat(self) -> object:
        return None

    def copy(self) -> MockLinear:
        m = MockLinear()
        m._domain = self._domain
        m._range = self._range
        return m


def _render(
    axis_maker: Callable[[object], object], scale: MockLinear, *, as_transition: bool
) -> str:
    root = create("svg").node()
    assert root is not None
    g = Element("g")
    root.append_child(g)
    sel = select_node(g)
    a = axis_maker(scale)
    a.tickValues([0.0, 0.5, 1.0])
    if as_transition:
        a(sel.transition())
    else:
        a(sel)
    return outer_html(root)


@pytest.mark.parametrize(
    "maker",
    [axisTop, axisRight, axisBottom, axisLeft],
    ids=["top", "right", "bottom", "left"],
)
def test_transition_matches_static_each_orientation(
    maker: Callable[[object], object],
) -> None:
    s = MockLinear()
    h1 = _render(maker, s, as_transition=False)
    s2 = MockLinear()
    h2 = _render(maker, s2, as_transition=True)
    assert h1 == h2


def test_parent_axis_fallback_on_enter_uses__axis_when_d3__axis_nulled() -> None:
    s = MockLinear()
    root = create("svg").node()
    assert root is not None
    g = Element("g")
    root.append_child(g)
    a0 = axisLeft(s).tickValues([0.0, 1.0])
    a0(select_node(g))  # stash overwrites; then prefer __axis path
    g.d3__axis = None
    g.__axis = lambda d: 0.25
    a1 = axisLeft(s).tickValues([0.0, 0.5, 1.0])
    a1(select_node(g).transition())
    out = outer_html(g)
    assert "tick" in out
    assert 'class="tick"' in out


def test_exit_transform_uses_stored_get_attribute_when_position_nonfinite() -> None:
    class Bad:
        def __init__(self) -> None:
            self._d = (0.0, 1.0)
            self._r = (0.0, 1.0)

        def __call__(self, x: object) -> float:
            v = float(x)
            if v == 0.5:
                return float("nan")
            d0, d1 = self._d
            r0, r1 = self._r
            t = (v - d0) / (d1 - d0)
            return r0 + t * (r1 - r0)

        def domain(self, d: object | None = None) -> object:
            if d is None:
                return self._d
            self._d = (float(d[0]), float(d[1]))  # type: ignore[index]
            return self

        def range(self, r: object | None = None) -> object:
            if r is None:
                return self._r
            self._r = (float(r[0]), float(r[1]))  # type: ignore[index]
            return self

        def ticks(self) -> list[float]:  # noqa: ANN003, ANN201
            return [0.0, 0.5, 1.0]

        def tickFormat(self) -> object:
            return None

        def copy(self) -> object:
            return self

    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    ax0 = axisLeft(Bad())  # uses [0, 0.5, 1.0] from scale.ticks
    ax0(select_node(g).transition())
    ax0.tickValues([0.0, 1.0])  # middle tick exits; NaN(0.5) → getAttribute
    ax0(select_node(g).transition())
    h = outer_html(g)
    assert "tick" in h


def test_tick_exit_path_reduces_tick_count() -> None:
    s = MockLinear()
    r = create("svg").node()
    g = Element("g")
    assert r is not None
    r.append_child(g)
    ax = axisLeft(s).tickValues([0.0, 0.5, 1.0])
    ax(select_node(g))
    h = outer_html(g)
    before = h.count('class="tick"')
    ax2 = axisLeft(s).tickValues([0.0, 1.0])
    ax2(select_node(g).transition())
    h2 = outer_html(g)
    after = h2.count('class="tick"')
    assert before == 3
    assert after == 2


def test_transition_api_stubs() -> None:
    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    sel = select_node(g)
    t = sel.transition()
    assert isinstance(t, Transition)
    t2: Transition = t.duration(300).delay(1).ease("cubic")
    assert t2.duration() == 300.0
    assert t2.delay() == 1.0
    assert t2.ease() == "cubic"
    t3: Transition = t2.transition()
    assert t3.selection() is t2.selection()
