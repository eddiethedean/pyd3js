# pyd3js-delaunay

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-delaunay.svg)](https://pypi.org/project/pyd3js-delaunay/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-delaunay)](https://pypi.org/project/pyd3js-delaunay/)
[![License](https://img.shields.io/pypi/l/pyd3js-delaunay.svg)](https://pypi.org/project/pyd3js-delaunay/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-delaunay`](https://github.com/d3/d3-delaunay) for **Delaunay triangulation** and **Voronoi** diagrams, aligned with the other **pyd3js** packages.

**Tracked upstream:** `d3-delaunay@6.0.4` — see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

**Requirements:** Python **3.10+**.

## What is d3-delaunay?

`d3-delaunay` builds a **Delaunay triangulation** from planar points and derives a **Voronoi diagram** (clipped to a viewport). It is the standard geometric core D3 uses for mesh and Voronoi layouts.

This package gives you the same workflow in Python: construct a **`Delaunay`**, optionally call **`voronoi(bounds)`**, and use render helpers that return **SVG path** strings (like upstream).

## What you get

- **`Delaunay`** and **`Voronoi`** matching the pinned upstream API (see compatibility matrix below).
- **Pure Python** tests: upstream Mocha suites are **ported to pytest** (no Node.js / `npm` gate).
- **`py.typed`** and type-checked public surface (see Development).

## Quickstart (verified)

Flat coordinates match upstream `new Delaunay(points)`:

```python
from array import array
from pyd3js_delaunay import Delaunay

coords = array("d", [0, 0, 1, 0, 0, 1])
d = Delaunay(coords)
v = d.voronoi([0, 0, 1, 1])
print(list(d.hull), v.render_bounds())
```

```text
[0, 2, 1] M0,0h1v1h-1Z
```

Point lists use **`Delaunay.from_points`** (same idea as JS **`Delaunay.from`**):

```python
from pyd3js_delaunay import Delaunay

d = Delaunay.from_points([[0, 0], [1, 0], [0, 1]])
print(list(d.triangles))
```

```text
[0, 2, 1]
```

If `bounds` is omitted, `d.voronoi()` uses the upstream default **`[0, 0, 960, 500]`**.

## Install

From PyPI:

```bash
pip install pyd3js-delaunay
```

This repo is a **uv** workspace. For local development:

```bash
uv sync --group dev
```

## Dependencies

Triangulation topology (`triangles`, `halfedges`, `hull`) comes from **[dylaunator](https://pypi.org/project/dylaunator/)** (Python port of [mapbox/delaunator](https://github.com/mapbox/delaunator)), which uses **[pyrobust-predicates](https://pypi.org/project/pyrobust-predicates/)** for adaptive-precision `orient2d` — the same dependency chain as JavaScript (`delaunator` → `robust-predicates`).

## Compatibility matrix

Symbols match upstream exports listed in [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md).

- `Delaunay` — [implemented]
- `Voronoi` — [implemented]

The Python package also exports **`__version__`**.

## JavaScript naming

Methods are **snake_case** in Python. **`Voronoi`** additionally exposes **camelCase aliases** (`renderCell`, `renderBounds`, `cellPolygon`, `cellPolygons`). Internal **`Path`** / **`Polygon`** helpers use canvas-style names (`moveTo`, `lineTo`, `closePath`).

## No Node / npm

Runtime and tests do **not** require Node.js, `npm`, or a JavaScript oracle.

## Documentation

- User guide: [`docs/USER_GUIDE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-delaunay/docs/USER_GUIDE.md)
- Upstream inventory & ported tests: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-delaunay/docs/UPSTREAM_API.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-delaunay/docs/CHANGELOG.md)
- Roadmap: [`docs/ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-delaunay/docs/ROADMAP.md)
- Updating the upstream pin: [`docs/UPSTREAM_UPDATE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-delaunay/docs/UPSTREAM_UPDATE.md)

## Development

```bash
uv run pytest packages/pyd3js-delaunay/package_tests -q
uv run ruff format packages/pyd3js-delaunay
uv run ruff check packages/pyd3js-delaunay
uv run ty check packages/pyd3js-delaunay
```

### Coverage (optional)

```bash
uv run pytest packages/pyd3js-delaunay/package_tests --cov=pyd3js_delaunay --cov-report=term-missing
```

### Build

```bash
uv build packages/pyd3js-delaunay
```

README and user guide Python snippets are checked by `package_tests/test_delaunay_docs_examples.py`.

## License

ISC — see [`LICENSE`](LICENSE).
