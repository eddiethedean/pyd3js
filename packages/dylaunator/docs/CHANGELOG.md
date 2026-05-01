# Changelog

All notable changes to **dylaunator** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.0

### Added

- Initial PyPI-ready release: Python port of **[mapbox/delaunator@v5.0.1](https://github.com/mapbox/delaunator/releases/tag/v5.0.1)** (half-edge mesh, `update`, `trianglesLen` / `triangles_len`).
- Dependency on **pyrobust-predicates** for `orient2d`-compatible robust tests.
- Vendored upstream `test/test.js` parity suite and JSON fixtures under `tests/fixtures/`.
- `docs/UPSTREAM_TESTS.md` provenance and typing marker (`py.typed`).
