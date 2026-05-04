from __future__ import annotations

from pyd3js_chord import ribbon


def foo(d):
    return d["foo"]


def test_ribbon_has_expected_defaults() -> None:
    r = ribbon()
    assert r.radius()({"radius": 42}) == 42
    assert r.startAngle()({"startAngle": 42}) == 42
    assert r.endAngle()({"endAngle": 42}) == 42
    assert r.source()({"source": {"name": "foo"}}) == {"name": "foo"}
    assert r.target()({"target": {"name": "foo"}}) == {"name": "foo"}
    assert r.context() is None


def test_ribbon_radius_sets_accessor() -> None:
    r = ribbon()
    assert r.radius(foo) is r
    assert r.radius() is foo
    assert r.radius(42) is r
    assert r.radius()() == 42


def test_ribbon_start_angle_sets_accessor() -> None:
    r = ribbon()
    assert r.startAngle(foo) is r
    assert r.startAngle() is foo
    assert r.startAngle(1.2) is r
    assert r.startAngle()() == 1.2


def test_ribbon_end_angle_sets_accessor() -> None:
    r = ribbon()
    assert r.endAngle(foo) is r
    assert r.endAngle() is foo
    assert r.endAngle(1.2) is r
    assert r.endAngle()() == 1.2


def test_ribbon_source_sets_accessor() -> None:
    r = ribbon()
    assert r.source(foo) is r
    assert r.source() is foo


def test_ribbon_target_sets_accessor() -> None:
    r = ribbon()
    assert r.target(foo) is r
    assert r.target() is foo


def test_ribbon_pad_angle_sets_accessor() -> None:
    r = ribbon()
    assert r.padAngle(foo) is r
    assert r.padAngle() is foo
    assert r.padAngle(1.2) is r
    assert r.padAngle()() == 1.2


def test_ribbon_context_sets_context() -> None:
    r = ribbon()
    assert r.context(None) is r
    assert r.context() is None
