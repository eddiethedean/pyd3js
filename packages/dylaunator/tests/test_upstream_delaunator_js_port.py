"""Port of mapbox/delaunator v5.0.1 `test/test.js` (node:test) to pytest."""

from __future__ import annotations

import json
from array import array
from pathlib import Path
from types import SimpleNamespace

import pytest

from dylaunator import Delaunator

from upstream_validate import validate

_FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_json(name: str) -> list:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def _flat(points: list[list[float]]) -> list[float]:
    return [c for p in points for c in p]


points = _load_json("ukraine.json")
issue13 = _load_json("issue13.json")
issue43 = _load_json("issue43.json")
issue44 = _load_json("issue44.json")
robustness1 = _load_json("robustness1.json")
robustness2 = _load_json("robustness2.json")
robustness3 = _load_json("robustness3.json")
robustness4 = _load_json("robustness4.json")


def test_triangulates_plain_array() -> None:
    d1 = Delaunator(_flat(points))
    d2 = Delaunator.from_points(points)
    assert list(d1.triangles) == list(d2.triangles)


def test_triangulates_typed_array() -> None:
    d1 = Delaunator(array("d", _flat(points)))
    d2 = Delaunator.from_points(points)
    assert list(d1.triangles) == list(d2.triangles)


def test_constructor_errors_on_non_numeric_flat_coords() -> None:
    with pytest.raises((TypeError, ValueError)):
        Delaunator(points)  # nested points, not flat floats


def test_js_invalid_typed_array_length() -> None:
    """JS `new Delaunator({ length: -1 })` — negative array-like length."""
    with pytest.raises(ValueError, match="Invalid typed array length"):
        Delaunator(SimpleNamespace(length=-1))


def test_js_public_surface_matches_upstream() -> None:
    """Upstream npm class: coords, triangles, halfedges, hull, trianglesLen, update, from."""
    assert hasattr(Delaunator, "from_points")
    d = Delaunator.from_points(points)
    for name in ("coords", "triangles", "halfedges", "hull"):
        assert hasattr(d, name)
    assert hasattr(d, "trianglesLen")
    assert callable(d.update)
    assert d.trianglesLen == d.triangles_len == 5133
    assert len(d.triangles) == d.trianglesLen

    p = [80.0, 220.0]
    d.coords[0] = p[0]
    d.coords[1] = p[1]
    new_points = [p] + points[1:]
    d.update()
    validate(new_points, d)
    assert d.trianglesLen == d.triangles_len == 5139
    assert len(d.triangles) == d.trianglesLen


def test_produces_correct_triangulation() -> None:
    validate(points)


def test_produces_correct_triangulation_after_modifying_coords_in_place() -> None:
    d = Delaunator.from_points(points)
    validate(points, d)
    assert d.triangles_len == 5133
    assert len(d.triangles) == d.triangles_len

    p = [80.0, 220.0]
    d.coords[0] = p[0]
    d.coords[1] = p[1]
    new_points = [p] + points[1:]

    d.update()
    validate(new_points, d)
    assert d.triangles_len == 5139
    assert len(d.triangles) == d.triangles_len


def test_issue_11() -> None:
    validate([[516, 661], [369, 793], [426, 539], [273, 525], [204, 694], [747, 750], [454, 390]])


def test_issue_13() -> None:
    validate(issue13)


def test_issue_24() -> None:
    validate(
        [
            [382, 302],
            [382, 328],
            [382, 205],
            [623, 175],
            [382, 188],
            [382, 284],
            [623, 87],
            [623, 341],
            [141, 227],
        ]
    )


def test_issue_43() -> None:
    validate(issue43)


def test_issue_44() -> None:
    validate(issue44)


def test_robustness() -> None:
    validate(robustness1)
    validate([[p[0] / 1e9, p[1] / 1e9] for p in robustness1])
    validate([[p[0] / 100, p[1] / 100] for p in robustness1])
    validate([[p[0] * 100, p[1] * 100] for p in robustness1])
    validate([[p[0] * 1e9, p[1] * 1e9] for p in robustness1])
    validate(robustness2[:100])
    validate(robustness2)
    validate(robustness3)
    validate(robustness4)


def test_returns_empty_triangulation_for_small_number_of_points() -> None:
    d = Delaunator.from_points([])
    assert list(d.triangles) == []
    assert list(d.hull) == []

    d = Delaunator.from_points(points[:1])
    assert list(d.triangles) == []
    assert list(d.hull) == [0]

    d = Delaunator.from_points(points[:2])
    assert list(d.triangles) == []
    assert set(d.hull) == {0, 1}
    assert len(d.hull) == 2


def test_returns_empty_triangulation_for_all_collinear_input() -> None:
    d = Delaunator.from_points([[0, 0], [1, 0], [3, 0], [2, 0]])
    assert list(d.triangles) == []
    assert set(d.hull) == {0, 1, 2, 3}
    assert len(d.hull) == 4


def test_supports_custom_point_format() -> None:
    d = Delaunator.from_points(
        [{"x": 5, "y": 5}, {"x": 7, "y": 5}, {"x": 7, "y": 6}],
        lambda p, *_: float(p["x"]),
        lambda p, *_: float(p["y"]),
    )
    assert list(d.triangles) == [0, 2, 1]
