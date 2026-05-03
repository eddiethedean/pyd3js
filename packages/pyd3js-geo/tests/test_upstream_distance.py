from pyd3js_geo import geoDistance

from test_support import assert_in_delta


def test_geo_distance_computes_great_arc_distance():
    assert geoDistance([0, 0], [0, 0]) == 0
    assert_in_delta(geoDistance([118 + 24 / 60, 33 + 57 / 60], [73 + 47 / 60, 40 + 38 / 60]), 3973 / 6371, 0.5)


def test_geo_distance_correctly_computes_small_distances():
    assert geoDistance([0, 0], [0, 1e-12]) > 0
