"""Port of upstream d3-axis `test/axis-test.js` (v3.0.0) — `it(...)` blocks as tests."""

from __future__ import annotations

from pyd3js_axis import axisLeft


def test_axis_left_scale_has_the_expected_defaults() -> None:
    s = object()
    a = axisLeft(s)
    assert a.scale() is s
    assert a.tickArguments() == []
    assert a.tickValues() is None
    assert a.tickFormat() is None
    assert a.tickSize() == 6
    assert a.tickSizeInner() == 6
    assert a.tickSizeOuter() == 6
    assert a.tickPadding() == 3


def test_axis_ticks_sets_the_tick_arguments() -> None:
    s = object()
    a = axisLeft(s).ticks(20)
    assert a.tickArguments() == [20]
    a = a.ticks()
    assert a.tickArguments() == []


def test_axis_tick_arguments_null_sets_to_empty() -> None:
    s = object()
    a = axisLeft(s).tickArguments(None)
    assert a.tickArguments() == []


def test_axis_tick_arguments_makes_a_defensive_copy() -> None:
    s = object()
    a = axisLeft(s).tickArguments([20])
    v = a.tickArguments()
    v.append(10)
    assert a.tickArguments() == [20]


def test_axis_tick_values_null_clears_explicit() -> None:
    s = object()
    a = axisLeft(s).tickValues([1, 2, 3])
    assert a.tickValues() == [1, 2, 3]
    a = a.tickValues([])
    assert a.tickValues() == []
    a = a.tickValues(None)
    assert a.tickValues() is None


def test_axis_tick_values_sets_explicit() -> None:
    s = object()
    a = axisLeft(s).tickValues([1, 2, 3])
    assert a.tickValues() == [1, 2, 3]


def test_axis_tick_values_makes_defensive_copy_of_input() -> None:
    s = object()
    v = [1, 2, 3]
    a = axisLeft(s).tickValues(v)
    v.append(4)
    assert a.tickValues() == [1, 2, 3]


def test_axis_tick_values_getter_makes_a_defensive_copy() -> None:
    s = object()
    a = axisLeft(s).tickValues([1, 2, 3])
    v = a.tickValues()
    assert v is not None
    v.append(4)
    assert a.tickValues() == [1, 2, 3]


def test_axis_tick_values_accepts_an_iterable() -> None:
    s = object()
    a = axisLeft(s).tickValues((1, 2, 3))  # JS: Set — Python tuple preserves order
    assert a.tickValues() == [1, 2, 3]
