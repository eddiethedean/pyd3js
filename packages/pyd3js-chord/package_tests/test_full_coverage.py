from __future__ import annotations

import pytest

from pyd3js_chord import chord, chordDirected, chordTranspose, ribbon, ribbonArrow
from pyd3js_path import path as make_path


def test_ribbon_arrow_head_radius_smoke() -> None:
    r = ribbonArrow()
    assert r.headRadius() is not None
    assert r.headRadius(5) is r


def test_ribbon_head_radius_not_on_plain_ribbon() -> None:
    with pytest.raises(AttributeError, match="headRadius"):
        ribbon().headRadius()


def test_chord_directed_and_transpose_smoke() -> None:
    m = [
        [1, 2],
        [3, 4],
    ]
    assert chordTranspose()(m).groups[0]["index"] in (0, 1)
    assert chordDirected()(m).groups[0]["index"] in (0, 1)


def test_chord_sorting_and_clear_sort_chords() -> None:
    m = [
        [0, 1, 2],
        [3, 0, 4],
        [5, 6, 0],
    ]
    c = chord()
    c.sortGroups(lambda a, b: b - a)
    c.sortSubgroups(lambda a, b: a - b)
    c.sortChords(lambda a, b: a - b)
    out = c(m)
    assert len(out.groups) == 3
    # Clear sortChords when passed None
    assert c.sortChords(None) is c
    assert c.sortChords() is None


def test_ribbon_pad_angle_branch_and_context_return_none() -> None:
    d = {
        "source": {"startAngle": 0.0, "endAngle": 0.01, "radius": 100.0},
        "target": {"startAngle": 1.0, "endAngle": 1.02, "radius": 90.0},
    }
    r = ribbonArrow().padAngle(0.1)
    s = r(d)
    assert s is not None and s.startswith("M")

    # If a context is provided, d3-ribbon returns None (draws into context).
    ctx = make_path()
    r2 = ribbon().context(ctx)
    assert r2(d) is None


def test_chord_directed_sort_subgroups_branch() -> None:
    m = [
        [0, 1, 2],
        [3, 0, 4],
        [5, 6, 0],
    ]
    cd = chordDirected().sortSubgroups(lambda a, b: b - a)
    out = cd(m)
    assert len(out.groups) == 3


def test_ribbon_extra_setters_and_reverse_angles() -> None:
    r = ribbon()
    assert r.sourceRadius(5) is r
    assert r.targetRadius(6) is r
    assert r.sourceRadius() is not None
    assert r.targetRadius() is not None

    # Reverse angles to hit the sa1 <= sa0 and ta1 <= ta0 branches.
    d = {
        "source": {"startAngle": 1.0, "endAngle": 0.0, "radius": 100.0},
        "target": {"startAngle": 2.0, "endAngle": 1.5, "radius": 90.0},
    }
    s = r.padAngle(0.2)(d)
    assert s is not None and s.startswith("M")

    # Forward angles to hit the sa1 > sa0 and ta1 > ta0 branches.
    d2 = {
        "source": {"startAngle": 0.0, "endAngle": 1.0, "radius": 100.0},
        "target": {"startAngle": 2.0, "endAngle": 2.5, "radius": 90.0},
    }
    s2 = r.padAngle(0.2)(d2)
    assert s2 is not None and s2.startswith("M")
