import math

import pytest
from pyd3js_geo import (
    geoAlbersUsa,
    geoAzimuthalEqualArea,
    geoAzimuthalEquidistant,
    geoConicConformal,
    geoConicEqualArea,
    geoConicEquidistant,
    geoEquirectangular,
    geoGnomonic,
    geoMercator,
    geoOrthographic,
    geoProjection,
    geoStereographic,
    geoTransverseMercator,
)

from test_support import assert_in_delta, load_json_gz



@pytest.fixture(scope="module")
def world():
    return load_json_gz("world_land_50m.geojson.gz")


@pytest.fixture(scope="module")
def us():
    return load_json_gz("us_land.geojson.gz")


def test_fit_extent_sphere_equirectangular():
    projection = geoEquirectangular()
    projection.fitExtent([[50, 50], [950, 950]], {"type": "Sphere"})
    assert_in_delta(projection.scale(), 900 / (2 * math.pi), 1e-6)
    assert_in_delta(projection.translate(), [500, 500], 1e-6)


@pytest.mark.parametrize(
    ("factory", "expected_scale", "expected_translate"),
    [
        (geoEquirectangular, 143.239449, [500, 492.000762]),
        (geoAzimuthalEqualArea, 228.357229, [496.353618, 479.684353]),
        (geoAzimuthalEquidistant, 153.559317, [485.272493, 452.093375]),
        (lambda: geoConicConformal().clipAngle(30).parallels([30, 60]).rotate([0, -45]), 625.567161, [444.206209, 409.910893]),
        (geoConicEqualArea, 145.862346, [500, 498.0114265]),
        (geoConicEquidistant, 123.085587, [500, 498.598401]),
        (lambda: geoGnomonic().clipAngle(45), 450.348233, [500.115138, 556.551304]),
        (geoMercator, 143.239449, [500, 481.549457]),
        (geoOrthographic, 451.406773, [503.769179, 498.593227]),
        (geoStereographic, 162.934379, [478.546293, 432.922534]),
        (geoTransverseMercator, 143.239449, [473.829551, 500]),
    ],
)
def test_fit_extent_world_projections(world, factory, expected_scale, expected_translate):
    projection = factory()
    projection.fitExtent([[50, 50], [950, 950]], world)
    assert_in_delta(projection.scale(), expected_scale, 1e-6)
    assert_in_delta(projection.translate(), expected_translate, 1e-6)


def test_fit_size_world_equirectangular_and_orthographic(world):
    projection = geoEquirectangular()
    projection.fitSize([900, 900], world)
    assert_in_delta(projection.scale(), 143.239449, 1e-6)
    assert_in_delta(projection.translate(), [450, 442.000762], 1e-6)
    projection = geoOrthographic()
    projection.fitSize([900, 900], world)
    assert_in_delta(projection.scale(), 451.406773, 1e-6)
    assert_in_delta(projection.translate(), [453.769179, 448.593227], 1e-6)


def test_fit_extent_usa_albers_usa(us):
    projection = geoAlbersUsa()
    projection.fitExtent([[50, 50], [950, 950]], us)
    assert_in_delta(projection.scale(), 1152.889035, 1e-6)
    assert_in_delta(projection.translate(), [533.52541, 496.232028], 1e-6)


@pytest.mark.parametrize(
    "geometry",
    [
        {"type": "Feature", "geometry": None},
        {"type": "MultiPoint", "coordinates": []},
        {"type": "MultiLineString", "coordinates": []},
        {"type": "MultiPolygon", "coordinates": []},
    ],
)
def test_fit_extent_null_geometries(geometry):
    projection = geoEquirectangular()
    projection.fitExtent([[50, 50], [950, 950]], geometry)
    scale = projection.scale()
    translate = projection.translate()
    assert not scale
    assert math.isnan(translate[0])
    assert math.isnan(translate[1])


def test_fit_extent_custom_projection(world):
    def raw(x, y):
        return [x, y**3]

    projection = geoProjection(raw)
    projection.fitExtent([[50, 50], [950, 950]], world)
    assert_in_delta(projection.scale(), 128.903525, 1e-6)
    assert_in_delta(projection.translate(), [500, 450.414357], 1e-6)


def test_fit_size_ignores_clip_extent(world):
    p1 = geoEquirectangular().fitSize([1000, 1000], world)
    p2 = geoEquirectangular().clipExtent([[100, 200], [700, 600]]).fitSize([1000, 1000], world)
    assert_in_delta(p1.scale(), p2.scale(), 1e-6)
    assert_in_delta(p1.translate(), p2.translate(), 1e-6)
    assert p1.clipExtent() is None
    assert p2.clipExtent() == [[100, 200], [700, 600]]


def test_fit_width_and_height(world, us):
    projection = geoEquirectangular().fitWidth(900, world)
    assert_in_delta(projection.scale(), 143.239449, 1e-6)
    assert_in_delta(projection.translate(), [450, 208.999023], 1e-6)
    projection = geoTransverseMercator().fitWidth(900, world)
    assert_in_delta(projection.scale(), 166.239257, 1e-6)
    assert_in_delta(projection.translate(), [419.627390, 522.256029], 1e-6)
    projection = geoAlbersUsa().fitWidth(900, us)
    assert_in_delta(projection.scale(), 1152.889035, 1e-6)
    assert_in_delta(projection.translate(), [483.52541, 257.736905], 1e-6)
    projection = geoEquirectangular().fitHeight(900, world)
    assert_in_delta(projection.scale(), 297.042711, 1e-6)
    assert_in_delta(projection.translate(), [933.187199, 433.411585], 1e-6)
    projection = geoAlbersUsa().fitHeight(900, us)
    assert_in_delta(projection.scale(), 1983.902059, 1e-6)
    assert_in_delta(projection.translate(), [832.054974, 443.516038], 1e-6)
