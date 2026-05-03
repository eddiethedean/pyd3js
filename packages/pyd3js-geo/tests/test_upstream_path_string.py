import math

from pyd3js_geo import geoEquirectangular, geoPath

from test_support import assert_path_equal



def equirectangular():
    return geoEquirectangular().scale(900 / math.pi).precision(0)


def render(obj):
    return geoPath().projection(equirectangular())(obj)


def test_geopath_string_renders_point_and_multipoint():
    assert_path_equal(
        render({"type": "Point", "coordinates": [-63, 18]}),
        "M165,160m0,4.500000a4.500000,4.500000 0 1,1 0,-9a4.500000,4.500000 0 1,1 0,9z",
    )
    assert_path_equal(
        geoPath().projection(equirectangular()).pointRadius(10)({"type": "Point", "coordinates": [-63, 18]}),
        "M165,160m0,10a10,10 0 1,1 0,-20a10,10 0 1,1 0,20z",
    )
    assert_path_equal(
        render({"type": "MultiPoint", "coordinates": [[-63, 18], [-62, 18], [-62, 17]]}),
        "M165,160m0,4.500000a4.500000,4.500000 0 1,1 0,-9a4.500000,4.500000 0 1,1 0,9z"
        "M170,160m0,4.500000a4.500000,4.500000 0 1,1 0,-9a4.500000,4.500000 0 1,1 0,9z"
        "M170,165m0,4.500000a4.500000,4.500000 0 1,1 0,-9a4.500000,4.500000 0 1,1 0,9z",
    )


def test_geopath_string_renders_lines_polygons_and_containers():
    polygon = {"type": "Polygon", "coordinates": [[[-63, 18], [-62, 18], [-62, 17], [-63, 18]]]}
    assert_path_equal(render({"type": "LineString", "coordinates": [[-63, 18], [-62, 18], [-62, 17]]}), "M165,160L170,160L170,165")
    assert_path_equal(render(polygon), "M165,160L170,160L170,165Z")
    assert_path_equal(render({"type": "GeometryCollection", "geometries": [polygon]}), "M165,160L170,160L170,165Z")
    assert_path_equal(render({"type": "Feature", "geometry": polygon}), "M165,160L170,160L170,165Z")
    assert_path_equal(render({"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": polygon}]}), "M165,160L170,160L170,165Z")


def test_geopath_string_line_then_point_does_not_share_state():
    path = geoPath().projection(equirectangular())
    assert_path_equal(path({"type": "LineString", "coordinates": [[-63, 18], [-62, 18], [-62, 17]]}), "M165,160L170,160L170,165")
    assert_path_equal(
        path({"type": "Point", "coordinates": [-63, 18]}),
        "M165,160m0,4.500000a4.500000,4.500000 0 1,1 0,-9a4.500000,4.500000 0 1,1 0,9z",
    )
