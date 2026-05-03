from pyd3js_geo import geoMercator, geoPath, geoTransverseMercator

from test_support import assert_in_delta, assert_path_equal


def test_mercator_clip_extent_null_sets_default_automatic_clip_extent():
    projection = geoMercator().translate([0, 0]).scale(1).clipExtent(None).precision(0)
    assert_path_equal(
        geoPath(projection)({"type": "Sphere"}),
        "M3.141593,-3.141593L3.141593,0L3.141593,3.141593L3.141593,3.141593L-3.141593,3.141593L-3.141593,3.141593L-3.141593,0L-3.141593,-3.141593L-3.141593,-3.141593L3.141593,-3.141593Z",
    )
    assert projection.clipExtent() is None


def test_mercator_center_sets_automatic_clip_extent():
    projection = geoMercator().translate([0, 0]).scale(1).center([10, 10]).precision(0)
    assert_path_equal(
        geoPath(projection)({"type": "Sphere"}),
        "M2.967060,-2.966167L2.967060,0.175426L2.967060,3.317018L2.967060,3.317018L-3.316126,3.317018L-3.316126,3.317019L-3.316126,0.175426L-3.316126,-2.966167L-3.316126,-2.966167L2.967060,-2.966167Z",
    )
    assert projection.clipExtent() is None


def test_mercator_clip_extent_intersects_specified_extent():
    projection = (
        geoMercator()
        .translate([0, 0])
        .scale(1)
        .clipExtent([[-10, -10], [10, 10]])
        .precision(0)
    )
    assert_path_equal(
        geoPath(projection)({"type": "Sphere"}),
        "M3.141593,-10L3.141593,0L3.141593,10L3.141593,10L-3.141593,10L-3.141593,10L-3.141593,0L-3.141593,-10L-3.141593,-10L3.141593,-10Z",
    )
    assert projection.clipExtent() == [[-10, -10], [10, 10]]


def test_mercator_rotate_does_not_affect_automatic_clip_extent():
    projection = geoMercator()
    obj = {
        "type": "MultiPoint",
        "coordinates": [
            [-82.35024908550241, 29.649391549778745],
            [-82.35014449996858, 29.65075946917633],
            [-82.34916073446641, 29.65070265688781],
            [-82.3492653331286, 29.64933474064504],
        ],
    }
    projection.fitExtent([[0, 0], [960, 600]], obj)
    assert_in_delta(projection.scale(), 20969742.365692537, 1e-3)
    assert_in_delta(
        projection.translate(), [30139734.76760269, 11371473.949706702], 1e-3
    )
    projection.rotate([0, 95]).fitExtent([[0, 0], [960, 600]], obj)
    assert_in_delta(projection.scale(), 35781690.650920525, 1e-3)
    assert_in_delta(
        projection.translate(), [75115911.95344563, 2586046.4116968135], 1e-3
    )


def test_transverse_mercator_clip_extent_null_sets_default_automatic_clip_extent():
    projection = (
        geoTransverseMercator().translate([0, 0]).scale(1).clipExtent(None).precision(0)
    )
    assert_path_equal(
        geoPath(projection)({"type": "Sphere"}),
        "M3.141593,3.141593L0,3.141593L-3.141593,3.141593L-3.141593,-3.141593L-3.141593,-3.141593L0,-3.141593L3.141593,-3.141593L3.141593,3.141593Z",
    )
    assert projection.clipExtent() is None


def test_transverse_mercator_center_sets_automatic_clip_extent():
    projection = (
        geoTransverseMercator().translate([0, 0]).scale(1).center([10, 10]).precision(0)
    )
    assert_path_equal(
        geoPath(projection)({"type": "Sphere"}),
        "M2.966,2.967L-0.175,2.967L-3.317,2.967L-3.317,-3.316L-3.317,-3.316L-0.175,-3.316L2.966,-3.316L2.966,2.967Z",
    )
    assert projection.clipExtent() is None


def test_transverse_mercator_clip_extent_intersects_specified_extent():
    projection = (
        geoTransverseMercator()
        .translate([0, 0])
        .scale(1)
        .clipExtent([[-10, -10], [10, 10]])
        .precision(0)
    )
    assert_path_equal(
        geoPath(projection)({"type": "Sphere"}),
        "M10,3.141593L0,3.141593L-10,3.141593L-10,-3.141593L-10,-3.141593L0,-3.141593L10,-3.141593L10,3.141593Z",
    )
    assert projection.clipExtent() == [[-10, -10], [10, 10]]
