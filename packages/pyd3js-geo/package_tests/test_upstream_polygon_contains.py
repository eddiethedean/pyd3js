"""Port of d3-geo `test/polygonContains-test.js` (degrees API via polygon_contains_degrees)."""

from __future__ import annotations

from pyd3js_geo import geoCircle
from pyd3js_geo.polygon_contains import polygon_contains_degrees as pc


def test_geo_polygon_contains_empty_point_returns_false():
    assert pc([], [0, 0]) is False


def test_geo_polygon_contains_simple_returns_expected():
    polygon = [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
    assert pc(polygon, [0.1, 2]) is False
    assert pc(polygon, [0.1, 0.1]) is True


def test_geo_polygon_contains_small_circle_returns_expected():
    polygon = geoCircle().radius(60)()["coordinates"]
    assert pc(polygon, [-180, 0]) is False
    assert pc(polygon, [1, 1]) is True


def test_geo_polygon_contains_wraps_longitudes():
    polygon = geoCircle().center([300, 0])()["coordinates"]
    assert pc(polygon, [300, 0]) is True
    assert pc(polygon, [-60, 0]) is True
    assert pc(polygon, [-420, 0]) is True


def test_geo_polygon_contains_south_pole_returns_expected():
    polygon = [[[-60, -80], [60, -80], [180, -80], [-60, -80]]]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, -85]) is True
    assert pc(polygon, [0, -90]) is True


def test_geo_polygon_contains_north_pole_returns_expected():
    polygon = [[[60, 80], [-60, 80], [-180, 80], [60, 80]]]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, 85]) is True
    assert pc(polygon, [0, 90]) is True
    assert pc(polygon, [-100, 90]) is True
    assert pc(polygon, [0, -90]) is False


def test_geo_polygon_contains_touching_pole_pole_returns_true_issue_105():
    polygon = [[[0, -30], [120, -30], [0, -90], [0, -30]]]
    assert pc(polygon, [0, -90]) is False
    assert pc(polygon, [-60, -90]) is False
    assert pc(polygon, [60, -90]) is False
    polygon2 = [[[0, 30], [-120, 30], [0, 90], [0, 30]]]
    assert pc(polygon2, [0, 90]) is False
    assert pc(polygon2, [-60, 90]) is False
    assert pc(polygon2, [60, 90]) is False


def test_geo_polygon_contains_south_hemisphere_poly():
    polygon = [[[0, 0], [10, -40], [-10, -40], [0, 0]]]
    assert pc(polygon, [0, -40.2]) is True
    assert pc(polygon, [0, -40.5]) is False


def test_geo_polygon_contains_large_near_origin_returns_expected():
    polygon = [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
    assert pc(polygon, [0.1, 0.1]) is False
    assert pc(polygon, [2, 0.1]) is True


def test_geo_polygon_contains_large_near_south_pole_returns_expected():
    polygon = [[[-60, 80], [60, 80], [180, 80], [-60, 80]]]
    assert pc(polygon, [0, 85]) is False
    assert pc(polygon, [0, 0]) is True


def test_geo_polygon_contains_large_near_north_pole_returns_expected():
    polygon = [[[60, -80], [-60, -80], [-180, -80], [60, -80]]]
    assert pc(polygon, [0, -85]) is False
    assert pc(polygon, [0, 0]) is True


def test_geo_polygon_contains_large_circle_returns_expected():
    polygon = geoCircle().radius(120)()["coordinates"]
    assert pc(polygon, [-180, 0]) is False
    assert pc(polygon, [-90, 0]) is True


def test_geo_polygon_contains_large_narrow_strip_hole_returns_expected():
    polygon = [
        [
            [-170, -1],
            [0, -1],
            [170, -1],
            [170, 1],
            [0, 1],
            [-170, 1],
            [-170, -1],
        ]
    ]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, 20]) is True


def test_geo_polygon_contains_large_narrow_equatorial_hole_returns_expected():
    circle = geoCircle().center([0, -90])
    ring0 = circle.radius(90 - 0.01)()["coordinates"][0]
    ring1 = list(reversed(circle.radius(90 + 0.01)()["coordinates"][0]))
    polygon = [ring0, ring1]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, -90]) is True


def test_geo_polygon_contains_large_narrow_equatorial_strip_returns_expected():
    circle = geoCircle().center([0, -90])
    ring0 = circle.radius(90 + 0.01)()["coordinates"][0]
    ring1 = list(reversed(circle.radius(90 - 0.01)()["coordinates"][0]))
    polygon = [ring0, ring1]
    assert pc(polygon, [0, -90]) is False
    assert pc(polygon, [0, 0]) is True


def test_geo_polygon_contains_ring_near_origin_returns_expected():
    ring0 = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
    ring1 = [[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6], [0.4, 0.4]]
    polygon = [ring0, ring1]
    assert pc(polygon, [0.5, 0.5]) is False
    assert pc(polygon, [0.1, 0.5]) is True


def test_geo_polygon_contains_ring_equatorial_returns_expected():
    ring0 = [[0, -10], [-120, -10], [120, -10], [0, -10]]
    ring1 = [[0, 10], [120, 10], [-120, 10], [0, 10]]
    polygon = [ring0, ring1]
    assert pc(polygon, [0, 20]) is False
    assert pc(polygon, [0, 0]) is True


def test_geo_polygon_contains_ring_excluding_both_poles_returns_expected():
    ring0 = list(reversed([[10, 10], [-10, 10], [-10, -10], [10, -10], [10, 10]]))
    ring1 = list(
        reversed([[170, 10], [170, -10], [-170, -10], [-170, 10], [170, 10]])
    )
    polygon = [ring0, ring1]
    assert pc(polygon, [0, 90]) is False
    assert pc(polygon, [0, 0]) is True


def test_geo_polygon_contains_ring_containing_both_poles_returns_expected():
    ring0 = [[10, 10], [-10, 10], [-10, -10], [10, -10], [10, 10]]
    ring1 = [[170, 10], [170, -10], [-170, -10], [-170, 10], [170, 10]]
    polygon = [ring0, ring1]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, 20]) is True


def test_geo_polygon_contains_ring_containing_south_pole_returns_expected():
    ring0 = [[10, 10], [-10, 10], [-10, -10], [10, -10], [10, 10]]
    ring1 = [[0, 80], [120, 80], [-120, 80], [0, 80]]
    polygon = [ring0, ring1]
    assert pc(polygon, [0, 90]) is False
    assert pc(polygon, [0, -90]) is True


def test_geo_polygon_contains_ring_containing_north_pole_returns_expected():
    ring0 = list(reversed([[10, 10], [-10, 10], [-10, -10], [10, -10], [10, 10]]))
    ring1 = list(reversed([[0, 80], [120, 80], [-120, 80], [0, 80]]))
    polygon = [ring0, ring1]
    assert pc(polygon, [0, -90]) is False
    assert pc(polygon, [0, 90]) is True


def test_geo_polygon_contains_self_intersecting_near_origin_returns_expected():
    polygon = [[[0, 0], [1, 0], [1, 3], [3, 3], [3, 1], [0, 1], [0, 0]]]
    assert pc(polygon, [15, 0.5]) is False
    assert pc(polygon, [12, 2]) is False
    assert pc(polygon, [0.5, 0.5]) is True
    assert pc(polygon, [2, 2]) is True


def test_geo_polygon_contains_self_intersecting_near_south_pole_returns_expected():
    polygon = [
        [
            [-10, -80],
            [120, -80],
            [-120, -80],
            [10, -85],
            [10, -75],
            [-10, -75],
            [-10, -80],
        ]
    ]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, -76]) is True
    assert pc(polygon, [0, -89]) is True


def test_geo_polygon_contains_self_intersecting_near_north_pole_returns_expected():
    polygon = [
        [
            [-10, 80],
            [-10, 75],
            [10, 75],
            [10, 85],
            [-120, 80],
            [120, 80],
            [-10, 80],
        ]
    ]
    assert pc(polygon, [0, 0]) is False
    assert pc(polygon, [0, 76]) is True
    assert pc(polygon, [0, 89]) is True


def test_geo_polygon_contains_hemisphere_touching_south_pole_returns_expected():
    polygon = geoCircle().radius(90)()["coordinates"]
    assert pc(polygon, [0, 0]) is True


def test_geo_polygon_contains_triangle_touching_south_pole_returns_expected():
    polygon = [[[180, -90], [-45, 0], [45, 0], [180, -90]]]
    assert pc(polygon, [-46, 0]) is False
    assert pc(polygon, [0, 1]) is False
    assert pc(polygon, [-90, -80]) is False
    assert pc(polygon, [-44, 0]) is True
    assert pc(polygon, [0, 0]) is True
    assert pc(polygon, [0, -30]) is True
    assert pc(polygon, [30, -80]) is True


def test_geo_polygon_contains_triangle_touching_south_pole2_returns_expected():
    polygon = [[[-45, 0], [45, 0], [180, -90], [-45, 0]]]
    assert pc(polygon, [-46, 0]) is False
    assert pc(polygon, [0, 1]) is False
    assert pc(polygon, [-90, -80]) is False
    assert pc(polygon, [-44, 0]) is True
    assert pc(polygon, [0, 0]) is True
    assert pc(polygon, [0, -30]) is True
    assert pc(polygon, [30, -80]) is True


def test_geo_polygon_contains_triangle_touching_south_pole3_returns_expected():
    polygon = [[[180, -90], [-135, 0], [135, 0], [180, -90]]]
    assert pc(polygon, [180, 0]) is False
    assert pc(polygon, [150, 0]) is False
    assert pc(polygon, [180, -30]) is False
    assert pc(polygon, [150, -80]) is False
    assert pc(polygon, [0, 0]) is True
    assert pc(polygon, [180, 1]) is True
    assert pc(polygon, [-90, -80]) is True


def test_geo_polygon_contains_triangle_touching_north_pole_returns_expected():
    polygon = [[[180, 90], [45, 0], [-45, 0], [180, 90]]]
    assert pc(polygon, [-90, 0]) is False
    assert pc(polygon, [0, -1]) is False
    assert pc(polygon, [0, -80]) is False
    assert pc(polygon, [-90, 1]) is False
    assert pc(polygon, [-90, 80]) is False
    assert pc(polygon, [-44, 10]) is True
    assert pc(polygon, [0, 10]) is True
    assert pc(polygon, [30, 80]) is True
