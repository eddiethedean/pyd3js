# pyd3js-geo user guide

This guide shows common usage patterns for `pyd3js-geo` with **runnable examples** and their **real outputs**.

All examples in this document are automatically verified by the test suite (`package_tests/test_geo_docs_examples.py`).

## Quickstart

Spherical helpers such as `geoDistance` and `geoInterpolate` use **degrees** for longitude and latitude, matching d3-geo.

```python
from pyd3js_geo import geoDistance, geoInterpolate

d = geoDistance([0, 0], [90, 0])
print(f"{d:.12f}")
f = geoInterpolate([0, 0], [90, 0])
p = f(0.5)
print(f"{p[0]:.12f} {p[1]:.12f}")
```

```text
1.570796326795
45.000000000000 0.000000000000
```

## Mercator path strings

`geoPath` turns GeoJSON objects into SVG path `d` strings in projected coordinates.

```python
from pyd3js_geo import geoMercator, geoPath

projection = geoMercator().translate([0, 0]).scale(1)
path = geoPath(projection)
line = {"type": "LineString", "coordinates": [[0, 0], [1, 0]]}
print(path(line))
```

```text
M0,0L0.017,0
```

## Rotation

`geoRotation` returns a callable that rotates spherical coordinates (degrees).

```python
from pyd3js_geo import geoRotation

rotate = geoRotation([90, 0])
r = rotate([0, 0])
print(f"[{r[0]}, {r[1]}]")
```

```text
[90.0, 0.0]
```
