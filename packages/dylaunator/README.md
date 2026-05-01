# dylaunator

Python port of [mapbox/delaunator](https://github.com/mapbox/delaunator) (v5.0.x API): fast Delaunay triangulation of 2D points using half-edge connectivity.

Robust orientation tests use [`pyrobust-predicates`](https://github.com/mourner/robust-predicates) (Python port), matching the JavaScript dependency chain used by `d3-delaunay`.

## Install

```bash
uv add dylaunator
```

## Usage

```python
from dylaunator import Delaunator

coords = [377, 479, 453, 434, 326, 387]
d = Delaunator(coords)
print(list(d.triangles))
```

## JS API mapping (mapbox/delaunator v5.0.x)

| JavaScript | Python |
|------------|--------|
| `new Delaunator(coords)` | `Delaunator(coords)` |
| `Delaunator.from(points, getX?, getY?)` | `Delaunator.from_points(points, fx?, fy?, that?)` — `from` is a Python keyword, so the static factory is named `from_points`. |
| `d.trianglesLen` | `d.triangles_len` **or** `d.trianglesLen` (same value; both names are supported). |
| `d.coords`, `d.triangles`, `d.halfedges`, `d.hull` | Same attribute names. |
| `d.update()` | `d.update()` |

Extra helpers (`flat_array`, `flat_iterable`, `default_get_x`, `default_get_y`) are exported for building flat coordinate buffers; they are not part of the published npm surface but mirror logic inside upstream `index.js`.

## Upstream test fixtures

Pytest mirrors [mapbox/delaunator@v5.0.1](https://github.com/mapbox/delaunator/tree/v5.0.1/test) `test/test.js` with JSON fixtures vendored under `tests/fixtures/` (same bytes as upstream `test/fixtures/*.json`).

## License

ISC (same as upstream `delaunator`).
