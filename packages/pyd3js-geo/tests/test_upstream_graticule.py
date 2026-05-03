from pyd3js_array import extent
from pyd3js_geo import geoGraticule



def test_graticule_precision_gets_and_sets():
    graticule = geoGraticule()
    assert graticule.precision() == 2.5
    graticule.precision(999)
    assert graticule.precision() == 999


def test_graticule_extent_sets_minor_and_major():
    graticule = geoGraticule().extent([[-90, -45], [90, 45]])
    assert graticule.extentMinor() == [[-90, -45], [90, 45]]
    assert graticule.extentMajor() == [[-90, -45], [90, 45]]
    reversed_graticule = geoGraticule().extent([[90, 45], [-90, -45]])
    assert reversed_graticule.extentMinor() == [[-90, -45], [90, 45]]
    assert reversed_graticule.extentMajor() == [[-90, -45], [90, 45]]


def test_graticule_extent_defaults():
    major = geoGraticule().extentMajor()
    assert major[0][0] == -180
    assert major[1][0] == 180
    assert major[0][1] == -90 + 1e-6
    assert major[1][1] == 90 - 1e-6
    minor = geoGraticule().extentMinor()
    assert minor[0][0] == -180
    assert minor[1][0] == 180
    assert minor[0][1] == -80 - 1e-6
    assert minor[1][1] == 80 + 1e-6


def test_graticule_step_gets_and_sets():
    graticule = geoGraticule().step([22.5, 22.5])
    assert graticule.stepMinor() == [22.5, 22.5]
    assert graticule.stepMajor() == [22.5, 22.5]
    assert geoGraticule().stepMinor() == [10, 10]
    assert geoGraticule().stepMajor() == [90, 360]


def test_graticule_lines_default_ranges():
    lines = geoGraticule().lines()
    longitude_lines = sorted(
        [line for line in lines if line["coordinates"][0][0] == line["coordinates"][1][0]],
        key=lambda line: line["coordinates"][0][0],
    )
    latitude_lines = sorted(
        [line for line in lines if line["coordinates"][0][1] == line["coordinates"][1][1]],
        key=lambda line: line["coordinates"][0][1],
    )
    assert longitude_lines[0]["coordinates"][0][0] == -180
    assert longitude_lines[-1]["coordinates"][0][0] == 170
    assert latitude_lines[0]["coordinates"][0][1] == -80
    assert latitude_lines[-1]["coordinates"][0][1] == 80


def test_graticule_lines_extents():
    lines = geoGraticule().lines()
    minor_longitudes = [
        line
        for line in lines
        if line["coordinates"][0][0] == line["coordinates"][1][0] and abs(line["coordinates"][0][0] % 90) > 1e-6
    ]
    major_longitudes = [
        line
        for line in lines
        if line["coordinates"][0][0] == line["coordinates"][1][0] and abs(line["coordinates"][0][0] % 90) < 1e-6
    ]
    latitudes = [line for line in lines if line["coordinates"][0][1] == line["coordinates"][1][1]]
    for line in minor_longitudes:
        assert extent(line["coordinates"], lambda p: p[1]) == [-80 - 1e-6, 80 + 1e-6]
    for line in major_longitudes:
        assert extent(line["coordinates"], lambda p: p[1]) == [-90 + 1e-6, 90 - 1e-6]
    for line in latitudes:
        assert extent(line["coordinates"], lambda p: p[0]) == [-180, 180]


def test_graticule_lines_and_outline_return_geojson():
    graticule = geoGraticule().extent([[-90, -45], [90, 45]]).step([45, 45]).precision(3)
    assert all(line["type"] == "LineString" for line in graticule.lines())
    assert graticule() == {"type": "MultiLineString", "coordinates": [line["coordinates"] for line in graticule.lines()]}
    assert geoGraticule().extentMajor([[-90, -45], [90, 45]]).precision(3).outline()["type"] == "Polygon"
