from pyd3js_geo import geoStream


class RecordingStream:
    def __init__(self):
        self.events = []

    def sphere(self):
        self.events.append(("sphere",))

    def point(self, x, y, z=None):
        self.events.append(("point", x, y, z))

    def lineStart(self):
        self.events.append(("lineStart",))

    def lineEnd(self):
        self.events.append(("lineEnd",))

    def polygonStart(self):
        self.events.append(("polygonStart",))

    def polygonEnd(self):
        self.events.append(("polygonEnd",))


def stream_events(obj):
    stream = RecordingStream()
    result = geoStream(obj, stream)
    assert result is None
    return stream.events


def test_stream_ignores_unknown_and_null_geometries():
    for obj in [
        {"type": "Unknown"},
        {"type": "Feature", "geometry": {"type": "Unknown"}},
        {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Unknown"}}]},
        {"type": "GeometryCollection", "geometries": [{"type": "Unknown"}]},
        None,
        {"type": "Feature", "geometry": None},
        {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": None}]},
        {"type": "GeometryCollection", "geometries": [None]},
    ]:
        assert stream_events(obj) == []


def test_stream_allows_empty_multi_geometries():
    for obj in [
        {"type": "MultiPoint", "coordinates": []},
        {"type": "MultiLineString", "coordinates": []},
        {"type": "MultiPolygon", "coordinates": []},
    ]:
        assert stream_events(obj) == []


def test_stream_sphere_to_sphere_event():
    assert stream_events({"type": "Sphere"}) == [("sphere",)]


def test_stream_point_to_point_event_with_z():
    assert stream_events({"type": "Point", "coordinates": [1, 2, 3]}) == [("point", 1, 2, 3)]


def test_stream_multipoint_to_point_events():
    assert stream_events({"type": "MultiPoint", "coordinates": [[1, 2, 3], [4, 5, 6]]}) == [
        ("point", 1, 2, 3),
        ("point", 4, 5, 6),
    ]


def test_stream_linestring_to_line_events():
    assert stream_events({"type": "LineString", "coordinates": [[1, 2, 3], [4, 5, 6]]}) == [
        ("lineStart",),
        ("point", 1, 2, 3),
        ("point", 4, 5, 6),
        ("lineEnd",),
    ]


def test_stream_multilinestring_to_line_events():
    assert stream_events(
        {"type": "MultiLineString", "coordinates": [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]}
    ) == [
        ("lineStart",),
        ("point", 1, 2, 3),
        ("point", 4, 5, 6),
        ("lineEnd",),
        ("lineStart",),
        ("point", 7, 8, 9),
        ("point", 10, 11, 12),
        ("lineEnd",),
    ]


def test_stream_polygon_to_polygon_events():
    assert stream_events(
        {
            "type": "Polygon",
            "coordinates": [[[1, 2, 3], [4, 5, 6], [1, 2, 3]], [[7, 8, 9], [10, 11, 12], [7, 8, 9]]],
        }
    ) == [
        ("polygonStart",),
        ("lineStart",),
        ("point", 1, 2, 3),
        ("point", 4, 5, 6),
        ("lineEnd",),
        ("lineStart",),
        ("point", 7, 8, 9),
        ("point", 10, 11, 12),
        ("lineEnd",),
        ("polygonEnd",),
    ]


def test_stream_multipolygon_to_polygon_events():
    assert stream_events(
        {"type": "MultiPolygon", "coordinates": [[[[1, 2, 3], [4, 5, 6], [1, 2, 3]]], [[[7, 8, 9], [10, 11, 12], [7, 8, 9]]]]}
    ) == [
        ("polygonStart",),
        ("lineStart",),
        ("point", 1, 2, 3),
        ("point", 4, 5, 6),
        ("lineEnd",),
        ("polygonEnd",),
        ("polygonStart",),
        ("lineStart",),
        ("point", 7, 8, 9),
        ("point", 10, 11, 12),
        ("lineEnd",),
        ("polygonEnd",),
    ]


def test_stream_feature_collection_and_geometry_collection():
    point = {"type": "Point", "coordinates": [1, 2, 3]}
    assert stream_events({"type": "Feature", "geometry": point}) == [("point", 1, 2, 3)]
    assert stream_events({"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": point}]}) == [
        ("point", 1, 2, 3)
    ]
    assert stream_events({"type": "GeometryCollection", "geometries": [point]}) == [("point", 1, 2, 3)]
