import math

from pyd3js_array import range as d3range
from pyd3js_geo import geoCentroid, geoCircle

from test_support import assert_in_delta, load_json_gz


def assert_nan_pair(point):
    assert all(math.isnan(value) for value in point)


def test_centroid_of_point_is_itself():
    for point in [[0, 0], [1, 1], [2, 3], [-4, -5]]:
        assert_in_delta(
            geoCentroid({"type": "Point", "coordinates": point}), point, 1e-6
        )


def test_centroid_of_points_is_spherical_average():
    assert_in_delta(
        geoCentroid(
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point", "coordinates": [0, 0]},
                    {"type": "Point", "coordinates": [1, 2]},
                ],
            }
        ),
        [0.499847, 1.000038],
        1e-6,
    )
    assert_in_delta(
        geoCentroid({"type": "MultiPoint", "coordinates": [[0, 0], [1, 2]]}),
        [0.499847, 1.000038],
        1e-6,
    )
    assert_in_delta(
        geoCentroid({"type": "MultiPoint", "coordinates": [[179, 0], [-179, 0]]}),
        [180, 0],
        1e-6,
    )


def test_centroid_antipodes_and_empty_points_are_ambiguous():
    assert_nan_pair(
        geoCentroid({"type": "MultiPoint", "coordinates": [[0, 0], [180, 0]]})
    )
    assert_nan_pair(
        geoCentroid(
            {"type": "MultiPoint", "coordinates": [[0, 0], [90, 0], [180, 0], [-90, 0]]}
        )
    )
    assert_nan_pair(geoCentroid({"type": "MultiPoint", "coordinates": []}))


def test_centroid_linestring_cases():
    assert_in_delta(
        geoCentroid({"type": "LineString", "coordinates": [[0, 0], [1, 0]]}),
        [0.5, 0],
        1e-6,
    )
    assert_in_delta(
        geoCentroid({"type": "LineString", "coordinates": [[0, 0], [0, 90]]}),
        [0, 45],
        1e-6,
    )
    assert_in_delta(
        geoCentroid({"type": "LineString", "coordinates": [[-1, -1], [1, 1]]}),
        [0, 0],
        1e-6,
    )
    assert_in_delta(
        geoCentroid({"type": "LineString", "coordinates": [[179, -1], [-179, 1]]}),
        [180, 0],
        1e-6,
    )
    assert_nan_pair(
        geoCentroid({"type": "LineString", "coordinates": [[180, 0], [0, 0]]})
    )
    assert_in_delta(
        geoCentroid({"type": "MultiLineString", "coordinates": [[[0, 0], [0, 2]]]}),
        [0, 1],
        1e-6,
    )


def test_centroid_zero_length_lines_and_empty_polygons_fall_back():
    assert_in_delta(
        geoCentroid({"type": "LineString", "coordinates": [[1, 1], [1, 1]]}),
        [1, 1],
        1e-6,
    )
    assert_in_delta(
        geoCentroid(
            {
                "type": "Polygon",
                "coordinates": [[[1, 1], [2, 1], [3, 1], [2, 1], [1, 1]]],
            }
        ),
        [2, 1.000076],
        1e-6,
    )
    assert_in_delta(
        geoCentroid(
            {"type": "Polygon", "coordinates": [[[1, 1], [1, 1], [1, 1], [1, 1]]]}
        ),
        [1, 1],
        1e-6,
    )


def test_centroid_polygon_surface_cases():
    assert_nan_pair(
        geoCentroid(
            {"type": "LineString", "coordinates": [[0, 0], [120, 0], [-120, 0], [0, 0]]}
        )
    )
    assert_in_delta(
        geoCentroid(
            {
                "type": "Polygon",
                "coordinates": [[[0, -90], [0, 0], [0, 90], [1, 0], [0, -90]]],
            }
        ),
        [0.5, 0],
        1e-6,
    )
    assert_in_delta(
        geoCentroid(
            {
                "type": "Polygon",
                "coordinates": [[[x, -60] for x in d3range(-180, 180 + 1 / 2, 1)]],
            }
        )[1],
        -90,
        1e-6,
    )
    assert_in_delta(
        geoCentroid(
            {
                "type": "Polygon",
                "coordinates": [[[0, -10], [0, 10], [10, 10], [10, -10], [0, -10]]],
            }
        ),
        [5, 0],
        1e-6,
    )


def test_centroid_multipolygon_and_circles():
    circle = geoCircle()
    assert_in_delta(
        geoCentroid(
            {
                "type": "MultiPolygon",
                "coordinates": [
                    circle.radius(45).center([90, 0])()["coordinates"],
                    circle.radius(60).center([-90, 0])()["coordinates"],
                ],
            }
        ),
        [-90, 0],
        1e-6,
    )
    assert_in_delta(
        geoCentroid(geoCircle().radius(5).center([30, 45])()), [30, 45], 1e-6
    )
    assert_in_delta(
        geoCentroid(geoCircle().radius(135).center([30, 45])()), [30, 45], 1e-6
    )


def test_centroid_container_precedence_and_sphere():
    assert_nan_pair(geoCentroid({"type": "Sphere"}))
    assert_in_delta(
        geoCentroid(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": [[1, 1], [1, 1]]},
            }
        ),
        [1, 1],
        1e-6,
    )
    assert_in_delta(
        geoCentroid(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[179, 0], [180, 0]],
                        },
                    },
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [0, 0]},
                    },
                ],
            }
        ),
        [179.5, 0],
        1e-6,
    )


def test_centroid_detailed_new_york_fixture():
    assert_in_delta(
        geoCentroid(load_json_gz("ny.json.gz")), [-73.93079, 40.69447], 1e-5
    )
