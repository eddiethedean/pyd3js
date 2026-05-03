import math

from pyd3js_geo import geoAlbers, geoEquirectangular, geoPath

from test_support import make_test_context


def path_events(projection, obj):
    context = make_test_context()
    geoPath().projection(projection).context(context)(obj)
    return context.result()


def equirectangular():
    return geoEquirectangular().scale(900 / math.pi).precision(0)


def test_geopath_projection_and_context_defaults():
    path = geoPath()
    assert path.projection() is None
    assert path.context() is None


def test_geopath_constructor_sets_projection_and_context():
    projection = geoAlbers()
    context = make_test_context()
    path = geoPath(projection, context)
    assert path.projection() is projection
    assert path.context() is context


def test_geopath_context_renders_point_and_multipoint():
    projection = equirectangular()
    assert path_events(projection, {"type": "Point", "coordinates": [-63, 18]}) == [
        {"type": "moveTo", "x": 170, "y": 160},
        {"type": "arc", "x": 165, "y": 160, "r": 4.5},
    ]
    assert path_events(
        projection,
        {"type": "MultiPoint", "coordinates": [[-63, 18], [-62, 18], [-62, 17]]},
    ) == [
        {"type": "moveTo", "x": 170, "y": 160},
        {"type": "arc", "x": 165, "y": 160, "r": 4.5},
        {"type": "moveTo", "x": 175, "y": 160},
        {"type": "arc", "x": 170, "y": 160, "r": 4.5},
        {"type": "moveTo", "x": 175, "y": 165},
        {"type": "arc", "x": 170, "y": 165, "r": 4.5},
    ]


def test_geopath_context_renders_lines_and_polygons():
    projection = equirectangular()
    polygon = {
        "type": "Polygon",
        "coordinates": [[[-63, 18], [-62, 18], [-62, 17], [-63, 18]]],
    }
    expected_polygon = [
        {"type": "moveTo", "x": 165, "y": 160},
        {"type": "lineTo", "x": 170, "y": 160},
        {"type": "lineTo", "x": 170, "y": 165},
        {"type": "closePath"},
    ]
    assert (
        path_events(
            projection,
            {"type": "LineString", "coordinates": [[-63, 18], [-62, 18], [-62, 17]]},
        )
        == expected_polygon[:-1]
    )
    assert path_events(projection, polygon) == expected_polygon
    assert (
        path_events(projection, {"type": "GeometryCollection", "geometries": [polygon]})
        == expected_polygon
    )
    assert (
        path_events(projection, {"type": "Feature", "geometry": polygon})
        == expected_polygon
    )
    assert (
        path_events(
            projection,
            {
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "geometry": polygon}],
            },
        )
        == expected_polygon
    )


def test_geopath_wraps_longitudes_and_identity_projection():
    projection = equirectangular()
    assert path_events(
        projection, {"type": "Point", "coordinates": [180 + 1e-6, 0]}
    ) == [
        {"type": "moveTo", "x": -415, "y": 250},
        {"type": "arc", "x": -420, "y": 250, "r": 4.5},
    ]
    assert path_events(
        None,
        {
            "type": "Polygon",
            "coordinates": [[[-63, 18], [-62, 18], [-62, 17], [-63, 18]]],
        },
    ) == [
        {"type": "moveTo", "x": -63, "y": 18},
        {"type": "lineTo", "x": -62, "y": 18},
        {"type": "lineTo", "x": -62, "y": 17},
        {"type": "closePath"},
    ]


def test_geopath_null_unknown_and_digits():
    path = geoPath()
    assert path() is None
    assert path(None) is None
    assert path({"type": "Unknown"}) is None
    assert path.digits() == 3
    assert path.digits(4) is path
    assert path.digits() == 4
    assert path.digits(0).digits() == 0
    assert geoPath().digits() == 3
    assert path.digits(None).digits() is None


def test_geopath_digits_respects_precision():
    line = {"type": "LineString", "coordinates": [[math.pi, math.e], [math.e, math.pi]]}
    assert geoPath().digits(0)(line) == "M3,3L3,3"
    assert geoPath().digits(1)(line) == "M3.1,2.7L2.7,3.1"
    assert geoPath().digits(2)(line) == "M3.14,2.72L2.72,3.14"
    assert geoPath().digits(3)(line) == "M3.142,2.718L2.718,3.142"
