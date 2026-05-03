import math

from pyd3js_geo import geoLength

from test_support import assert_in_delta


def test_geo_length_point_and_multipoint_return_zero():
    assert_in_delta(geoLength({"type": "Point", "coordinates": [0, 0]}), 0, 1e-6)
    assert_in_delta(geoLength({"type": "MultiPoint", "coordinates": [[0, 1], [2, 3]]}), 0, 1e-6)


def test_geo_length_linestring_returns_sum_of_great_arc_segments():
    assert_in_delta(geoLength({"type": "LineString", "coordinates": [[-45, 0], [45, 0]]}), math.pi / 2, 1e-6)
    assert_in_delta(geoLength({"type": "LineString", "coordinates": [[-45, 0], [-30, 0], [-15, 0], [0, 0]]}), math.pi / 4, 1e-6)


def test_geo_length_multilinestring_returns_sum():
    assert_in_delta(
        geoLength({"type": "MultiLineString", "coordinates": [[[-45, 0], [-30, 0]], [[-15, 0], [0, 0]]]}),
        math.pi / 6,
        1e-6,
    )


def test_geo_length_polygon_perimeter_and_holes():
    assert_in_delta(
        geoLength({"type": "Polygon", "coordinates": [[[0, 0], [3, 0], [3, 3], [0, 3], [0, 0]]]}),
        0.157008,
        1e-6,
    )
    assert_in_delta(
        geoLength(
            {
                "type": "Polygon",
                "coordinates": [
                    [[0, 0], [3, 0], [3, 3], [0, 3], [0, 0]],
                    [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]],
                ],
            }
        ),
        0.209354,
        1e-6,
    )


def test_geo_length_multipolygon_returns_sum():
    assert_in_delta(
        geoLength({"type": "MultiPolygon", "coordinates": [[[[0, 0], [3, 0], [3, 3], [0, 3], [0, 0]]]]}),
        0.157008,
        1e-6,
    )
    assert_in_delta(
        geoLength(
            {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[0, 0], [3, 0], [3, 3], [0, 3], [0, 0]]],
                    [[[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]]],
                ],
            }
        ),
        0.209354,
        1e-6,
    )


def test_geo_length_feature_and_geometry_collections():
    assert_in_delta(
        geoLength(
            {
                "type": "FeatureCollection",
                "features": [
                    {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[-45, 0], [0, 0]]}},
                    {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[0, 0], [45, 0]]}},
                ],
            }
        ),
        math.pi / 2,
        1e-6,
    )
    assert_in_delta(
        geoLength(
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "GeometryCollection", "geometries": [{"type": "LineString", "coordinates": [[-45, 0], [0, 0]]}]},
                    {"type": "LineString", "coordinates": [[0, 0], [45, 0]]},
                ],
            }
        ),
        math.pi / 2,
        1e-6,
    )
