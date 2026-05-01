# Upstream d3-delaunay API inventory

Pinned upstream version: `d3-delaunay@6.0.4` (see `upstream_lock.json` at repo root).

## Exports

These are the symbols exposed by [`d3-delaunay` `src/index.js`](https://github.com/d3/d3-delaunay/blob/v6.0.4/src/index.js):

- `Delaunay`
- `Voronoi`

## Upstream tests (ported)

Upstream `d3-delaunay@6.0.4` runs Mocha tests from `test/**/*-test.js`. This package ports those tests to pure-Python pytest:

- Upstream `test/delaunay-test.js` → `tests/test_upstream_d3_delaunay_js_port_delaunay.py`
- Upstream `test/voronoi-test.js` → `tests/test_upstream_d3_delaunay_js_port_voronoi.py`
