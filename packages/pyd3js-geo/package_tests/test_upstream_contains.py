from pyd3js_geo import geoCircle, geoContains, geoInterpolate


def test_contains_sphere_and_points():
    assert geoContains({"type": "Sphere"}, [0, 0]) is True
    assert geoContains({"type": "Point", "coordinates": [0, 0]}, [0, 0]) is True
    assert geoContains({"type": "Point", "coordinates": [1, 2]}, [1, 2]) is True
    assert geoContains({"type": "Point", "coordinates": [0, 0]}, [0, 1]) is False
    assert (
        geoContains({"type": "MultiPoint", "coordinates": [[0, 0], [1, 2]]}, [1, 2])
        is True
    )
    assert (
        geoContains({"type": "MultiPoint", "coordinates": [[0, 0], [1, 2]]}, [1, 3])
        is False
    )


def test_contains_linestring_great_circle_path():
    line = {"type": "LineString", "coordinates": [[0, 0], [1, 2]]}
    assert geoContains(line, [0, 0]) is True
    assert geoContains(line, [1, 2]) is True
    assert geoContains(line, geoInterpolate([0, 0], [1, 2])(0.3)) is True
    assert geoContains(line, geoInterpolate([0, 0], [1, 2])(1.3)) is False
    assert geoContains(line, geoInterpolate([0, 0], [1, 2])(-0.3)) is False


def test_contains_linestring_epsilon_points():
    epsilon = 1e-6
    line = [[0, 0], [0, 10], [10, 10], [10, 0]]
    for point in [[0, 5], [epsilon, 5], [0, epsilon], [epsilon, epsilon]]:
        assert geoContains({"type": "LineString", "coordinates": line}, point)
    for point in [[epsilon * 10, 5], [epsilon * 10, epsilon]]:
        assert not geoContains({"type": "LineString", "coordinates": line}, point)


def test_contains_multilinestring():
    assert (
        geoContains(
            {
                "type": "MultiLineString",
                "coordinates": [[[0, 0], [1, 2]], [[2, 3], [4, 5]]],
            },
            [2, 3],
        )
        is True
    )
    assert (
        geoContains(
            {
                "type": "MultiLineString",
                "coordinates": [[[0, 0], [1, 2]], [[2, 3], [4, 5]]],
            },
            [5, 6],
        )
        is False
    )


def test_contains_polygon_and_hole():
    polygon = geoCircle().radius(60)()
    assert geoContains(polygon, [1, 1]) is True
    assert geoContains(polygon, [-180, 0]) is False
    outer = geoCircle().radius(60)()["coordinates"][0]
    inner = geoCircle().radius(3)()["coordinates"][0]
    polygon_with_hole = {"type": "Polygon", "coordinates": [outer, inner]}
    assert geoContains(polygon_with_hole, [1, 1]) is False
    assert geoContains(polygon_with_hole, [5, 0]) is True
    assert geoContains(polygon_with_hole, [65, 0]) is False


def test_contains_multipolygon_and_collections():
    p1 = geoCircle().radius(6)()["coordinates"]
    p2 = geoCircle().radius(6).center([90, 0])()["coordinates"]
    polygon = {"type": "MultiPolygon", "coordinates": [p1, p2]}
    assert geoContains(polygon, [1, 0]) is True
    assert geoContains(polygon, [90, 1]) is True
    assert geoContains(polygon, [90, 45]) is False
    collection = {
        "type": "GeometryCollection",
        "geometries": [
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "LineString", "coordinates": [[-45, 0], [0, 0]]}
                ],
            },
            {"type": "LineString", "coordinates": [[0, 0], [45, 0]]},
        ],
    }
    assert geoContains(collection, [-45, 0]) is True
    assert geoContains(collection, [45, 0]) is True
    assert geoContains(collection, [12, 25]) is False


def test_contains_features_and_null():
    feature = {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": [[0, 0], [45, 0]]},
    }
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            feature,
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": [[-45, 0], [0, 0]]},
            },
        ],
    }
    assert geoContains(feature, [45, 0]) is True
    assert geoContains(feature, [12, 25]) is False
    assert geoContains(feature_collection, [45, 0]) is True
    assert geoContains(feature_collection, [-45, 0]) is True
    assert geoContains(feature_collection, [12, 25]) is False
    assert geoContains(None, [0, 0]) is False
