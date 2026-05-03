# pyd3js-delaunay user guide

Runnable examples for **Delaunay** triangulation and **Voronoi** diagrams (aligned with **d3-delaunay@6.0.4**).

Examples in this file are verified by `package_tests/test_delaunay_docs_examples.py` (paired `python` + `text` blocks).

## Flat coordinates (`new Delaunay` in JS)

```python
from array import array
from pyd3js_delaunay import Delaunay

coords = array("d", [0, 0, 1, 0, 0, 1])
d = Delaunay(coords)
print(list(d.triangles))
```

```text
[0, 2, 1]
```

## `Delaunay.from_points` (JS `Delaunay.from`)

```python
from pyd3js_delaunay import Delaunay

d = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]])
print(list(d.triangles))
```

```text
[0, 2, 1, 2, 3, 1]
```

## Voronoi default bounds

Omitting bounds matches upstream `delaunay.voronoi()` default **`[0, 0, 960, 500]`**.

```python
from pyd3js_delaunay import Delaunay

v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]]).voronoi()
print(v.xmin, v.ymin, v.xmax, v.ymax)
```

```text
0.0 0.0 960.0 500.0
```

## `find` — nearest site

```python
from pyd3js_delaunay import Delaunay

d = Delaunay.from_points([[0, 0], [300, 0], [0, 300], [300, 300], [100, 100]])
print(d.find(49, 49), d.find(51, 51))
```

```text
0 4
```

## Render helpers (SVG path strings)

```python
from pyd3js_delaunay import Delaunay

d = Delaunay.from_points([[0, 0], [1, 0], [0, 1]])
s = d.render()
print(s is not None, "M" in (s or ""))
```

```text
True True
```
