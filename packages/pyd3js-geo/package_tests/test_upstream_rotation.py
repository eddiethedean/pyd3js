from pyd3js_geo import geoRotation

from test_support import assert_in_delta


def test_rotation_90_degrees_only_rotates_longitude():
    rotation = geoRotation([90, 0])([0, 0])
    assert_in_delta(rotation[0], 90, 1e-6)
    assert_in_delta(rotation[1], 0, 1e-6)


def test_rotation_90_degrees_wraps_at_antimeridian():
    rotation = geoRotation([90, 0])([150, 0])
    assert_in_delta(rotation[0], -120, 1e-6)
    assert_in_delta(rotation[1], 0, 1e-6)


def test_rotation_longitude_and_latitude():
    rotation = geoRotation([-45, 45])([0, 0])
    assert_in_delta(rotation[0], -54.73561, 1e-6)
    assert_in_delta(rotation[1], 30, 1e-6)


def test_rotation_inverse_longitude_and_latitude():
    rotation = geoRotation([-45, 45]).invert([-54.73561, 30])
    assert_in_delta(rotation[0], 0, 1e-6)
    assert_in_delta(rotation[1], 0, 1e-6)


def test_identity_rotation_constrains_longitudes():
    rotate = geoRotation([0, 0])
    assert rotate([180, 0])[0] == 180
    assert rotate([-180, 0])[0] == -180
    assert rotate([360, 0])[0] == 0
    assert_in_delta(rotate([2562, 0])[0], 42, 1e-10)
    assert_in_delta(rotate([-2562, 0])[0], -42, 1e-10)
