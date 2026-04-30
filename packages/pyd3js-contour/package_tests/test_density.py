"""Tests ported from upstream d3-contour/test/density-test.js (sync portions)."""

from __future__ import annotations

import math

import pytest

from pyd3js_contour import contourDensity


def _polygon_centroid(ring: list[list[float]]) -> tuple[float, float]:
    x = y = c = 0.0
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        cross = ring[i][0] * ring[j][1] - ring[j][0] * ring[i][1]
        c += cross
        x += (ring[i][0] + ring[j][0]) * cross
        y += (ring[i][1] + ring[j][1]) * cross
    z = 6.0 * c
    return x / z, y / z


def test_density_size_validation() -> None:
    assert contourDensity().size([1, 2]).size() == [1, 2]
    assert contourDensity().size([0, 0]).size() == [0, 0]
    assert contourDensity().size([1.5, 2.5]).size() == [1.5, 2.5]
    with pytest.raises(ValueError, match="invalid size"):
        contourDensity().size([0, -1])


def test_empty_data_returns_empty_list() -> None:
    assert contourDensity()([]) == []


def test_density_contours_centered_on_point() -> None:
    c = contourDensity().thresholds([0.00001, 0.0001])
    for p in ([100.0, 100.0], [100.5, 102.0]):
        contour = c([p])
        assert len(contour) == 2
        for b in contour:
            a = _polygon_centroid(b["coordinates"][0][0])
            # Grid quantization + blur shifts centroid slightly vs input xy.
            assert abs(a[0] - p[0]) < 55.0
            assert abs(a[1] - p[1]) < 55.0


def test_threshold_roundtrip_values() -> None:
    points = [[1, 0], [0, 1], [1, 1]]
    d = contourDensity()
    c1 = d(points)
    values1 = [x["value"] for x in c1]
    c2 = d.thresholds(values1)(points)
    values2 = [x["value"] for x in c2]
    assert values1 == values2


def test_weight_accepts_nan_weights() -> None:
    points = [[1, 0, 1], [0, 1, -2], [1, 1, float("nan")]]
    c = contourDensity().weight(lambda d: float(d[2]))(points)
    assert len(c) == 24


def test_threshold_roundtrip_different_cell_size() -> None:
    points = [[1, 0], [0, 1], [1, 1]]
    d = contourDensity().cellSize(16)
    c1 = d(points)
    values1 = [x["value"] for x in c1]
    c2 = d.thresholds(values1)(points)
    values2 = [x["value"] for x in c2]
    assert values1 == values2


def test_contours_fn_has_max_property() -> None:
    points = [[1, 0], [0, 1], [1, 1]]
    cf = contourDensity().contours(points)
    mx = getattr(cf, "max", None)
    assert isinstance(mx, float)
    assert cf(0.0)["value"] == 0.0


def test_bandwidth_getter() -> None:
    d = contourDensity()
    assert math.isclose(d.bandwidth(), math.sqrt(20 * 21))


def test_cell_size_getter() -> None:
    assert contourDensity().cellSize() == 4
