# Changelog

All notable changes to `pyd3js-geo` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.0 — 2026-05-03

### Added

- Python port of `d3-geo@3.1.1` public API (`geoPath`, streams, projections, graticule, clip helpers, etc.); pin tracked in monorepo `upstream_lock.json` (`d3-geo@3.1.1`).
- Ported upstream JS tests under `package_tests/test_upstream_*.py` (opt-in via `PYD3JS_GEO_FULL_UPSTREAM=1`), including full numerical parity and **100% line coverage** on `pyd3js_geo` when that mode is enabled.
- GeoJSON as plain `dict` / `list` structures; dependency on `pyd3js-array` for shared numeric helpers (`>=0.1.0`).
- **Topic guides** in `docs/guides/` (getting started, projections, GeoJSON/paths, spherical geometry, development and parity) with index `docs/guides/README.md`.
- `polygon_contains_degrees()` helper for spherical polygon-in-polygon tests (degrees API); `test_upstream_polygon_contains.py` ports upstream `polygonContains` coverage.
- Path **context** tests in place of browser PNG snapshot tests.

### Fixed

- Projection **`center` / `rotate` / `angle`** use ECMAScript-style `% 360` (`ecma_mod` in `math.py`) so negative longitudes and composite **`geoAlbersUsa`** match d3-geo (Python’s floor modulo was wrong for values like `center([-0.6, 38.7])`).

### Documentation

- `README.md` — badges, install, compatibility matrix, testing and coverage commands; links to guides.
- `docs/` — changelog, roadmap, upstream API inventory, user guide (`USER_GUIDE.md` examples verified by tests).
- Package layout: `package_tests/` naming aligned with other workspace packages; `py.typed` for typing consumers.
