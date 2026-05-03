import math

from pyd3js_geo import geoEquirectangular, geoPath

from test_support import assert_in_delta


def equirectangular():
    return geoEquirectangular().scale(900 / math.pi).precision(0)


def test_geopath_area_of_polygons_and_sphere():
    path = geoPath().projection(equirectangular())
    assert (
        path.area(
            {
                "type": "Polygon",
                "coordinates": [[[100, 0], [100, 1], [101, 1], [101, 0], [100, 0]]],
            }
        )
        == 25
    )
    assert (
        path.area(
            {
                "type": "Polygon",
                "coordinates": [
                    [[100, 0], [100, 1], [101, 1], [101, 0], [100, 0]],
                    [
                        [100.2, 0.2],
                        [100.8, 0.2],
                        [100.8, 0.8],
                        [100.2, 0.8],
                        [100.2, 0.2],
                    ],
                ],
            }
        )
        == 16
    )
    assert path.area({"type": "Sphere"}) == 1620000


def test_geopath_bounds_of_polygons_and_sphere():
    path = geoPath().projection(equirectangular())
    assert path.bounds(
        {
            "type": "Polygon",
            "coordinates": [[[100, 0], [100, 1], [101, 1], [101, 0], [100, 0]]],
        }
    ) == [
        [980, 245],
        [985, 250],
    ]
    assert path.bounds(
        {
            "type": "Polygon",
            "coordinates": [
                [[100, 0], [100, 1], [101, 1], [101, 0], [100, 0]],
                [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]],
            ],
        }
    ) == [[980, 245], [985, 250]]
    assert path.bounds({"type": "Sphere"}) == [[-420, -200], [1380, 700]]


def test_geopath_centroid_points_lines_polygons():
    path = geoPath().projection(equirectangular())
    assert path.centroid({"type": "Point", "coordinates": [0, 0]}) == [480, 250]
    assert all(
        math.isnan(value)
        for value in path.centroid({"type": "MultiPoint", "coordinates": []})
    )
    assert path.centroid(
        {"type": "MultiPoint", "coordinates": [[-122, 37], [-74, 40]]}
    ) == [-10, 57.5]
    assert path.centroid({"type": "LineString", "coordinates": [[100, 0], [0, 0]]}) == [
        730,
        250,
    ]
    assert_in_delta(
        path.centroid(
            {"type": "LineString", "coordinates": [[-122, 37], [-74, 40], [-100, 0]]}
        ),
        [17.389135, 103.563545],
        1e-6,
    )
    assert path.centroid(
        {
            "type": "Polygon",
            "coordinates": [[[100, 0], [100, 1], [101, 1], [101, 0], [100, 0]]],
        }
    ) == [
        982.5,
        247.5,
    ]
    assert path.centroid({"type": "Sphere"}) == [480, 250]


def test_geopath_measure_geometries():
    path = geoPath()
    assert path.measure({"type": "Point", "coordinates": [0, 0]}) == 0
    assert (
        path.measure(
            {"type": "MultiPoint", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0]]}
        )
        == 0
    )
    assert (
        path.measure(
            {"type": "LineString", "coordinates": [[0, 0], [0, 1], [1, 1], [1, 0]]}
        )
        == 3
    )
    assert (
        path.measure(
            {
                "type": "MultiLineString",
                "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0]]],
            }
        )
        == 3
    )
    assert (
        path.measure(
            {
                "type": "Polygon",
                "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
            }
        )
        == 4
    )
    assert (
        path.measure(
            {
                "type": "Polygon",
                "coordinates": [
                    [[-1, -1], [-1, 2], [2, 2], [2, -1], [-1, -1]],
                    [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]],
                ],
            }
        )
        == 16
    )
