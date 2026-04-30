from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay import Delaunay


def _v() -> tuple[Delaunay, object]:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    return d, v


def test_clip_segment_flip_and_reject_cases(require_node_mesh: None) -> None:
    _d, v = _v()
    # Force flip branch by passing c0 < c1.
    s = v._clip_segment(2.0, 0.5, -1.0, 0.5, v._regioncode(2.0, 0.5), v._regioncode(-1.0, 0.5))
    assert s is not None

    # Reject when both endpoints are outside on the same side (c0 & c1).
    s2 = v._clip_segment(-1.0, -1.0, -2.0, -3.0, v._regioncode(-1.0, -1.0), v._regioncode(-2.0, -3.0))
    assert s2 is None


def test_clip_segment_div_zero_guards(require_node_mesh: None) -> None:
    _d, v = _v()
    # Horizontal segment clipped against top/bottom -> dy == 0 guard.
    c0 = v._regioncode(-1.0, 2.0)
    c1 = v._regioncode(2.0, 2.0)
    assert v._clip_segment(-1.0, 2.0, 2.0, 2.0, c0, c1) is None

    # Vertical segment clipped against left/right -> dx == 0 guard.
    c0 = v._regioncode(2.0, -1.0)
    c1 = v._regioncode(2.0, 2.0)
    assert v._clip_segment(2.0, -1.0, 2.0, 2.0, c0, c1) is None


def test_project_none_paths(require_node_mesh: None) -> None:
    _d, v = _v()
    # top
    assert v._project(0.5, 0.0, 0.0, -1.0) is None
    # bottom
    assert v._project(0.5, 1.0, 0.0, 1.0) is None
    # right
    assert v._project(1.0, 0.5, 1.0, 0.0) is None
    # left
    assert v._project(0.0, 0.5, -1.0, 0.0) is None


def test_edge_p_none_and_insertion_path(require_node_mesh: None, monkeypatch: pytest.MonkeyPatch) -> None:
    _d, v = _v()
    # p is None early return.
    assert v._edge(0, 0b0100, 0b0010, None, 0) == 0

    # Force insertion branch by stubbing contains to True.
    monkeypatch.setattr(v, "contains", lambda *_args, **_kwargs: True)
    p: list[float] = []
    j = v._edge(0, 0b0100, 0b0110, p, 0)
    assert j >= 0
    assert len(p) >= 2


def test_clip_infinite_and_simplify_loop(require_node_mesh: None, monkeypatch: pytest.MonkeyPatch) -> None:
    d, v = _v()
    # For a hull point, `_clip` should go through the infinite clipping path.
    assert v._clip(d.hull[0]) is not None

    # Exercise simplify removal loop directly.
    pts = [0.0, 0.0, 0.0, 1.0, 0.0, 2.0, 1.0, 2.0]
    simplified = v._simplify(pts)
    assert simplified is not None

