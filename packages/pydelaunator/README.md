# pydelaunator

Python port of [mapbox/delaunator](https://github.com/mapbox/delaunator) (v5.0.x API): fast Delaunay triangulation of 2D points using half-edge connectivity.

Robust orientation tests use [`pyrobust-predicates`](https://github.com/mourner/robust-predicates) (Python port), matching the JavaScript dependency chain used by `d3-delaunay`.

## Install

```bash
uv add pydelaunator
```

## Usage

```python
from pydelaunator import Delaunator

coords = [377, 479, 453, 434, 326, 387]
d = Delaunator(coords)
print(list(d.triangles))
```

## License

ISC (same as upstream `delaunator`).
