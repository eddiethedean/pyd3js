import math

import pytest
from pyd3js_geo import (
    geoAlbers,
    geoAlbersUsa,
    geoAzimuthalEqualArea,
    geoAzimuthalEquidistant,
    geoConicConformal,
    geoConicEqualArea,
    geoConicEquidistant,
    geoEqualEarth,
    geoEquirectangular,
    geoGnomonic,
    geoIdentity,
    geoMercator,
    geoOrthographic,
    geoPath,
    geoStereographic,
    geoTransverseMercator,
)

from test_support import assert_in_delta, assert_path_equal, assert_projection_equal



def test_equirectangular_returns_expected_results():
    projection = geoEquirectangular().translate([0, 0]).scale(1)
    assert_projection_equal(projection, [0, 0], [0, 0])
    assert_projection_equal(projection, [-180, 0], [-math.pi, 0])
    assert_projection_equal(projection, [180, 0], [math.pi, 0])
    assert_projection_equal(projection, [0, 30], [0, -math.pi / 6])
    assert_projection_equal(projection, [30, -30], [math.pi / 6, math.pi / 6])


def test_equirectangular_rotations():
    projection = geoEquirectangular().rotate([30, 0]).translate([0, 0]).scale(1)
    assert_projection_equal(projection, [0, 0], [math.pi / 6, 0])
    assert_projection_equal(projection, [-30, 30], [0, -math.pi / 6])
    projection = geoEquirectangular().rotate([30, 30]).translate([0, 0]).scale(1)
    assert_projection_equal(projection, [0, 0], [0.5880026035475674, -0.44783239692893245])
    projection = geoEquirectangular().rotate([0, 0, 30]).translate([0, 0]).scale(1)
    assert_projection_equal(projection, [30, -30], [0.6947382761967031, 0.21823451436745964])


def test_stereographic_returns_expected_results():
    projection = geoStereographic().translate([0, 0]).scale(1)
    assert_projection_equal(projection, [0, 0], [0, 0])
    assert_projection_equal(projection, [-90, 0], [-1, 0])
    assert_projection_equal(projection, [90, 0], [1, 0])
    assert_projection_equal(projection, [0, -90], [0, 1])
    assert_projection_equal(projection, [0, 90], [0, -1])


def test_identity_returns_and_transforms_points():
    identity = geoIdentity().translate([0, 0]).scale(1)
    assert_projection_equal(identity, [0, 0], [0, 0])
    assert_projection_equal(identity, [-180, 0], [-180, 0])
    identity = geoIdentity().translate([100, 10]).scale(2)
    assert_projection_equal(identity, [30, 30], [160, 70])
    assert_projection_equal(identity.reflectX(True), [3, 7], [94, 24])
    assert_projection_equal(identity.reflectY(True), [3, 7], [94, -4])


def test_geopath_identity_respects_transform_and_clip_extent():
    identity = geoIdentity().translate([0, 0]).scale(1)
    path = geoPath().projection(identity)
    assert path({"type": "LineString", "coordinates": [[0, 0], [10, 10]]}) == "M0,0L10,10"
    identity.translate([30, 90]).scale(2).reflectY(True)
    assert path({"type": "LineString", "coordinates": [[0, 0], [10, 10]]}) == "M30,90L50,70"
    identity.clipExtent([[35, 76], [45, 86]])
    assert path({"type": "LineString", "coordinates": [[0, 0], [10, 10]]}) == "M35,85L44,76"


def test_projection_angle_and_reflect():
    projection = geoGnomonic().scale(1).translate([0, 0])
    assert projection.angle() == 0
    assert_projection_equal(projection, [10, 0], [0.17632698070846498, 0])
    projection.angle(30)
    assert_in_delta(projection.angle(), 30)
    assert_projection_equal(projection, [10, 0], [0.1527036446661393, -0.08816349035423247])
    projection = geoGnomonic().scale(1).translate([0, 0]).reflectX(True)
    assert projection.reflectX() is True
    assert_projection_equal(projection, [10, 0], [-0.17632698070846498, 0])


def test_azimuthal_projections_do_not_crash_on_antipode():
    for point in [
        geoAzimuthalEqualArea()([180, 0]),
        geoAzimuthalEqualArea()([-180, 0]),
        geoAzimuthalEquidistant()([180, 0]),
    ]:
        assert abs(point[0]) < math.inf
        assert abs(point[1]) < math.inf


@pytest.mark.parametrize(
    "factory",
    [
        geoAlbers,
        geoAzimuthalEqualArea,
        geoAzimuthalEquidistant,
        geoConicConformal,
        lambda: geoConicConformal().parallels([20, 30]),
        lambda: geoConicConformal().parallels([30, 30]),
        lambda: geoConicEqualArea().parallels([20, 30]),
        lambda: geoConicEqualArea().parallels([-30, 30]),
        lambda: geoConicEquidistant().parallels([20, 30]),
        geoEquirectangular,
        geoEqualEarth,
        geoGnomonic,
        geoMercator,
        geoOrthographic,
        geoStereographic,
        geoTransverseMercator,
    ],
)
def test_projection_and_invert_are_symmetric(factory):
    projection = factory()
    for point in [[0, 0], [30.3, 24.1], [-10, 42], [-2, -5]]:
        assert_projection_equal(projection, point, projection(point))


def test_albers_usa_expected_points():
    projection = geoAlbersUsa()
    assert_projection_equal(projection, [-122.4194, 37.7749], [107.4, 214.1], 0.1)
    assert_projection_equal(projection, [-74.0059, 40.7128], [794.6, 176.5], 0.1)
    assert_projection_equal(projection, [-95.9928, 36.1540], [488.8, 298.0], 0.1)
    assert_projection_equal(projection, [-149.9003, 61.2181], [171.2, 446.9], 0.1)
    assert_projection_equal(projection, [-157.8583, 21.3069], [298.5, 451.0], 0.1)
    assert projection([2.3522, 48.8566]) is None


def test_rotation_of_degenerate_polygon_does_not_break():
    projection = geoMercator().rotate([-134.300, 25.776]).scale(750).translate([0, 0])
    assert_path_equal(
        geoPath(projection)(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [125.67351590459046, -14.17673705310531],
                        [125.67351590459046, -14.173276873687367],
                        [125.67351590459046, -14.173276873687367],
                        [125.67351590459046, -14.169816694269425],
                        [125.67351590459046, -14.17673705310531],
                    ]
                ],
            }
        ),
        "M-111.644162,-149.157654L-111.647235,-149.203744L-111.647235,-149.203744L-111.650307,-149.249835Z",
    )
