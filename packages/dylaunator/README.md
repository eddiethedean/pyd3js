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

## Upstream test fixtures

Pytest mirrors [mapbox/delaunator@v5.0.1](https://github.com/mapbox/delaunator/tree/v5.0.1/test) `test/test.js` with JSON fixtures vendored under `tests/fixtures/` (same bytes as upstream `test/fixtures/*.json`).

## License

ISC (same as upstream `delaunator`).
