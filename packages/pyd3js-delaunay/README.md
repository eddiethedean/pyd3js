# pyd3js-delaunay

Python port of [`d3-delaunay`](https://github.com/d3/d3-delaunay) for triangulations and Voronoi diagrams, aligned with the rest of the `pyd3js` packages.

**Tracked version:** `d3-delaunay@6.0.4` — see [`upstream_lock.json`](../../upstream_lock.json).

## Install

```bash
uv add pyd3js-delaunay
```

## Usage

```python
from array import array
from pyd3js_delaunay import Delaunay

coords = array("d", [0, 0, 1, 0, 0, 1])
d = Delaunay(coords)
v = d.voronoi([0, 0, 1, 1])
print(list(d.hull), v.render_bounds())
```

Triangulation topology (`triangles`, `halfedges`, `hull`) is computed with **[dylaunator](https://github.com/mapbox/delaunator)** (Python port; PyPI name `dylaunator`), which depends on **[pyrobust-predicates](https://github.com/mourner/robust-predicates)** for adaptive-precision `orient2d`, matching the JavaScript dependency chain (`delaunator` → `robust-predicates`).

## Compatibility matrix

Symbols correspond to [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md).

- `Delaunay` — [implemented]
- `Voronoi` — [implemented]

## No Node / npm dependencies

This package is **pure Python**. It does not require Node.js, `npm`, or an oracle subprocess to run tests or to use at runtime.

## License

ISC — see [`LICENSE`](LICENSE).
