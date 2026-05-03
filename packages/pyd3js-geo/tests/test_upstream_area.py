import math

import pytest
from pyd3js_array import range as d3range
from pyd3js_geo import geoArea, geoCircle, geoGraticule

from test_support import assert_in_delta



def stripes(a, b):
    rings = []
    for i, d in enumerate([a, b]):
        stripe = [[x, d] for x in d3range(-180, 180, 0.1)]
        stripe.append(stripe[0])
        rings.append(list(reversed(stripe)) if i else stripe)
    return {"type": "Polygon", "coordinates": rings}


@pytest.mark.parametrize(
    ("geometry", "expected"),
    [
        ({"type": "Point", "coordinates": [0, 0]}, 0),
        ({"type": "MultiPoint", "coordinates": [[0, 1], [2, 3]]}, 0),
        ({"type": "LineString", "coordinates": [[0, 1], [2, 3]]}, 0),
        ({"type": "MultiLineString", "coordinates": [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]}, 0),
        ({"type": "Sphere"}, 4 * math.pi),
        ({"type": "GeometryCollection", "geometries": [{"type": "Sphere"}]}, 4 * math.pi),
        ({"type": "Feature", "geometry": {"type": "Sphere"}}, 4 * math.pi),
        (
            {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Sphere"}}]},
            4 * math.pi,
        ),
    ],
)
def test_area_zero_and_container_geometries(geometry, expected):
    assert geoArea(geometry) == expected


@pytest.mark.parametrize(
    ("coordinates", "expected", "delta"),
    [
        (
            [
                [
                    [-64.66070178517852, 18.33986913231323],
                    [-64.66079715091509, 18.33994007490749],
                    [-64.66074946804680, 18.33994007490749],
                    [-64.66070178517852, 18.33986913231323],
                ]
            ],
            4.890516e-13,
            1e-13,
        ),
        ([[[0, 0], [0, 90], [90, 0], [0, 0]]], math.pi / 2, 1e-6),
        ([[[0, 0], [0, 90], [90, 0], [0, -90], [0, 0]]], math.pi, 1e-6),
        ([[[0, 0], [-90, 0], [180, 0], [90, 0], [0, 0]]], 2 * math.pi, 1e-6),
        ([[[0, 0], [90, 0], [180, 0], [-90, 0], [0, 0]]], 2 * math.pi, 1e-6),
        ([[[0, 0], [0, 90], [180, 0], [0, -90], [0, 0]]], 2 * math.pi, 1e-6),
        ([[[0, 0], [0, -90], [180, 0], [0, 90], [0, 0]]], 2 * math.pi, 1e-6),
    ],
)
def test_area_polygon_cases(coordinates, expected, delta):
    assert_in_delta(geoArea({"type": "Polygon", "coordinates": coordinates}), expected, delta)


def test_area_polygon_zero_area():
    assert geoArea(
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [96.79142432523281, 5.262704519048153],
                    [96.81065389253769, 5.272455576551362],
                    [96.82988345984256, 5.272455576551362],
                    [96.81065389253769, 5.272455576551362],
                    [96.79142432523281, 5.262704519048153],
                ]
            ],
        }
    ) == 0


@pytest.mark.parametrize(
    ("radius", "center", "expected", "delta"),
    [
        (90, None, 2 * math.pi, 1e-5),
        (60, None, math.pi, 1e-5),
        (60, [0, 90], math.pi, 1e-5),
        (45, None, math.pi * (2 - math.sqrt(2)), 1e-5),
        (45, [0, 90], math.pi * (2 - math.sqrt(2)), 1e-5),
        (45, [0, -90], math.pi * (2 - math.sqrt(2)), 1e-5),
        (135, None, math.pi * (2 + math.sqrt(2)), 1e-5),
        (135, [0, 90], math.pi * (2 + math.sqrt(2)), 1e-5),
        (135, [0, -90], math.pi * (2 + math.sqrt(2)), 1e-5),
        (1e-6, None, 0, 1e-6),
        (180 - 1e-6, None, 4 * math.pi, 1e-6),
    ],
)
def test_area_circles(radius, center, expected, delta):
    circle = geoCircle().radius(radius).precision(0.1)
    if center is not None:
        circle.center(center)
    assert_in_delta(geoArea(circle()), expected, delta)


def test_area_graticule_outlines():
    assert_in_delta(geoArea(geoGraticule().extent([[-180, -90], [180, 90]]).outline()), 4 * math.pi, 1e-5)
    assert_in_delta(geoArea(geoGraticule().extent([[-180, 0], [180, 90]]).outline()), 2 * math.pi, 1e-5)
    assert_in_delta(geoArea(geoGraticule().extent([[0, 0], [90, 90]]).outline()), math.pi / 2, 1e-5)


def test_area_polygon_with_holes_and_stripes():
    circle = geoCircle().precision(0.1)
    assert_in_delta(
        geoArea(
            {
                "type": "Polygon",
                "coordinates": [
                    circle.radius(60)()["coordinates"][0],
                    list(reversed(circle.radius(45)()["coordinates"][0])),
                ],
            }
        ),
        math.pi * (math.sqrt(2) - 1),
        1e-5,
    )
    assert_in_delta(geoArea(stripes(45, -45)), math.pi * 2 * math.sqrt(2), 1e-5)
    assert_in_delta(geoArea(stripes(-45, 45)), math.pi * 2 * (2 - math.sqrt(2)), 1e-5)
    assert_in_delta(geoArea(stripes(45, 30)), math.pi * (math.sqrt(2) - 1), 1e-5)


def test_area_multipolygon_two_hemispheres():
    assert geoArea(
        {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [-90, 0], [180, 0], [90, 0], [0, 0]]],
                [[[0, 0], [90, 0], [180, 0], [-90, 0], [0, 0]]],
            ],
        }
    ) == 4 * math.pi
