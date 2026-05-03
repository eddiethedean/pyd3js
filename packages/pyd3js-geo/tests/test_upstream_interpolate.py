from pyd3js_geo import geoInterpolate

from test_support import assert_in_delta


def test_geo_interpolate_same_point_returns_point():
    assert geoInterpolate([140.63289, -29.95101], [140.63289, -29.95101])(0.5) == [140.63289, -29.95101]


def test_geo_interpolate_equator():
    assert_in_delta(geoInterpolate([10, 0], [20, 0])(0.5), [15, 0], 1e-6)


def test_geo_interpolate_meridian():
    assert_in_delta(geoInterpolate([10, -20], [10, 40])(0.5), [10, 10], 1e-6)
