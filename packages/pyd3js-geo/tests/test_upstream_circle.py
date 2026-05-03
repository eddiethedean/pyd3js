from pyd3js_array import range as d3range
from pyd3js_geo import geoCircle

from test_support import assert_in_delta


def test_circle_generates_polygon():
    circle = geoCircle()()
    assert circle["type"] == "Polygon"
    assert len(circle["coordinates"]) == 1


def test_circle_default_coordinates_match_upstream_shape():
    expected = [
        [[-78.69007, -90]],
    ]
    assert_in_delta(geoCircle()()["coordinates"][0][0], expected[0][0], 1e-5)


def test_circle_center_north_pole():
    circle = geoCircle().center([0, 90])()
    assert circle["type"] == "Polygon"
    # Default precision is 6°; ring samples every 6° along the equator (d3 `geoCircle`).
    assert_in_delta(
        circle["coordinates"],
        [[[x - 360 if x >= 180 else x, 0] for x in d3range(360, -1, -6)]],
        1e-6,
    )


def test_circle_center_with_zero_radius_starts_at_center():
    circle = geoCircle().center([45, 45]).radius(0)()
    assert circle["type"] == "Polygon"
    assert_in_delta(circle["coordinates"][0][0], [45, 45], 1e-6)


def test_circle_first_and_last_points_are_coincident():
    coordinates = (
        geoCircle().center([0, 0]).radius(0.02).precision(45)()["coordinates"][0]
    )
    assert_in_delta(coordinates[0], coordinates[-1], 1e-6)
