# Upstream d3-delaunay API inventory

Pinned upstream version: **`d3-delaunay@6.0.4`** (see [`upstream_lock.json`](../../upstream_lock.json) at the monorepo root).

Upstream reference: [`d3/d3-delaunay` `v6.0.4`](https://github.com/d3/d3-delaunay/tree/v6.0.4).

## Exports

These are the symbols exposed by [`d3-delaunay` `src/index.js`](https://github.com/d3/d3-delaunay/blob/v6.0.4/src/index.js):

- `Delaunay`
- `Voronoi`

## Python package layout

| Upstream (JS) | This package (Python) |
| --- | --- |
| `src/delaunay.js` | `pyd3js_delaunay.delaunay` — class `Delaunay` |
| `src/voronoi.js` | `pyd3js_delaunay.voronoi` — class `Voronoi`, `CellPolygon` |
| `src/path.js` | `pyd3js_delaunay.path` — class `Path` |
| `src/polygon.js` | `pyd3js_delaunay.polygon` — class `Polygon` |
| `src/index.js` | `pyd3js_delaunay.__init__` — re-exports `Delaunay`, `Voronoi`, `__version__` |

## Naming vs upstream

- **`Delaunay.from` (JS)** → **`Delaunay.from_points`** (Python), with the same optional `fx`, `fy`, and `that` behavior for array-likes and iterables.
- Methods are **snake_case** in Python; **`Voronoi`** keeps **camelCase aliases** on select methods for parity with d3 (`renderCell`, `renderBounds`, `cellPolygon`, `cellPolygons`).
- **`Path`** / **`Polygon`** use canvas-style method names (`moveTo`, `lineTo`, `closePath`) like upstream.

## Upstream tests (ported)

Upstream runs Mocha from `test/**/*-test.js` (`npm test` in upstream). This repo ports those suites to **pure-Python pytest** (no Node):

| Upstream file | Pytest module |
| --- | --- |
| [`test/delaunay-test.js`](https://github.com/d3/d3-delaunay/blob/v6.0.4/test/delaunay-test.js) | `package_tests/test_upstream_d3_delaunay_js_port_delaunay.py` |
| [`test/voronoi-test.js`](https://github.com/d3/d3-delaunay/blob/v6.0.4/test/voronoi-test.js) | `package_tests/test_upstream_d3_delaunay_js_port_voronoi.py` |

Additional tests under `package_tests/` cover clipping branches, path helpers, coverage edges, and README / user guide examples.

## Releases

See [`CHANGELOG.md`](CHANGELOG.md). Packaging metadata lives in `pyproject.toml` (`project.urls`, `license-files`, sdist includes).
