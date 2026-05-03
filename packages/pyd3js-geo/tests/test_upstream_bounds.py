import math

import pytest
from pyd3js_geo import geoBounds

from test_support import assert_in_delta


def assert_all_nan(bounds):
    assert all(math.isnan(value) for point in bounds for value in point)


def test_bounds_feature_featurecollection_and_geometrycollection():
    assert geoBounds(
        {
            "type": "Feature",
            "geometry": {"type": "MultiPoint", "coordinates": [[-123, 39], [-122, 38]]},
        }
    ) == [
        [-123, 38],
        [-122, 39],
    ]
    assert geoBounds(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-123, 39]},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-122, 38]},
                },
            ],
        }
    ) == [[-123, 38], [-122, 39]]
    assert geoBounds(
        {
            "type": "GeometryCollection",
            "geometries": [
                {"type": "Point", "coordinates": [-123, 39]},
                {"type": "Point", "coordinates": [-122, 38]},
            ],
        }
    ) == [[-123, 38], [-122, 39]]


def test_bounds_linestring_cases():
    assert geoBounds(
        {"type": "LineString", "coordinates": [[-123, 39], [-122, 38]]}
    ) == [[-123, 38], [-122, 39]]
    assert geoBounds(
        {"type": "LineString", "coordinates": [[-30, -20], [130, 40]]}
    ) == geoBounds({"type": "LineString", "coordinates": [[130, 40], [-30, -20]]})
    assert geoBounds(
        {"type": "LineString", "coordinates": [[0, 0], [0, 1], [0, 60]]}
    ) == [[0, 0], [0, 60]]
    assert geoBounds(
        {"type": "LineString", "coordinates": [[0, 0], [1, 0], [60, 0]]}
    ) == [[0, 0], [60, 0]]
    assert_in_delta(
        geoBounds({"type": "LineString", "coordinates": [[-45, 60], [45, 60]]}),
        [[-45, 60], [45, 67.792345]],
        1e-6,
    )
    assert_in_delta(
        geoBounds({"type": "LineString", "coordinates": [[-45, -60], [45, -60]]}),
        [[-45, -67.792345], [45, -60]],
        1e-6,
    )


def test_bounds_multipoint_antimeridian_cases():
    assert geoBounds(
        {"type": "MultiPoint", "coordinates": [[-123, 39], [-122, 38]]}
    ) == [[-123, 38], [-122, 39]]
    assert geoBounds(
        {"type": "MultiPoint", "coordinates": [[-179, 39], [179, 38]]}
    ) == [[179, 38], [-179, 39]]
    assert geoBounds(
        {"type": "MultiPoint", "coordinates": [[-1, 0], [1, 0], [-179, 39], [179, 38]]}
    ) == [[-1, 0], [-179, 39]]
    assert geoBounds(
        {"type": "MultiPoint", "coordinates": [[178, 38], [179, 39], [-179, 37]]}
    ) == [[178, 37], [-179, 39]]


def test_bounds_polygon_cases():
    assert_in_delta(
        geoBounds(
            {
                "type": "Polygon",
                "coordinates": [[[-123, 39], [-122, 39], [-122, 38], [-123, 39]]],
            }
        ),
        [[-123, 38], [-122, 39.001067]],
        1e-6,
    )
    assert geoBounds(
        {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
        }
    ) == [
        [-180, -90],
        [180, 90],
    ]
    assert_in_delta(
        geoBounds(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-170, 80],
                        [0, 80],
                        [170, 80],
                        [170, -80],
                        [0, -80],
                        [-170, -80],
                        [-170, 80],
                    ]
                ],
            }
        ),
        [[-170, -89.119552], [170, 89.119552]],
        1e-6,
    )
    assert geoBounds(
        {
            "type": "Polygon",
            "coordinates": [[[-60, -80], [60, -80], [180, -80], [-60, -80]]],
        }
    ) == [
        [-180, -90],
        [180, -80],
    ]


def test_bounds_sphere_and_nested_collection():
    assert geoBounds({"type": "Sphere"}) == [[-180, -90], [180, 90]]
    assert geoBounds(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "GeometryCollection",
                        "geometries": [
                            {"type": "Point", "coordinates": [-120, 47]},
                            {"type": "Point", "coordinates": [-119, 46]},
                        ],
                    },
                }
            ],
        }
    ) == [[-120, 46], [-119, 47]]


@pytest.mark.parametrize(
    "geometry",
    [
        {"type": "Feature", "geometry": None},
        {"type": "MultiPoint", "coordinates": []},
        {"type": "MultiLineString", "coordinates": []},
        {"type": "MultiPolygon", "coordinates": []},
    ],
)
def test_bounds_null_geometries_return_nan(geometry):
    assert_all_nan(geoBounds(geometry))
