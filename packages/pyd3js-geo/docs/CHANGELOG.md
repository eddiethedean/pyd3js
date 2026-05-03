# Changelog

All notable changes to `pyd3js-geo` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.0 — 2026-05-02

### Added

- Python port of `d3-geo@3.1.1` public API (`geoPath`, streams, projections, graticule, clip helpers, etc.).
- Ported upstream JS tests under `package_tests/test_upstream_*.py` (opt-in via `PYD3JS_GEO_FULL_UPSTREAM=1`).
- GeoJSON as plain `dict` / `list` structures; dependency on `pyd3js-array` for numeric helpers where shared.
- Documentation and packaging aligned with `pyd3js-array` standards:
  - `docs/` (changelog, roadmap, upstream API inventory, user guide).
  - `README.md` (badges, install, compatibility matrix, testing/coverage commands).
  - Renamed `tests/` → `package_tests/` for consistency with other workspace packages.
  - Package-level `.gitignore` and `pyproject.toml` metadata (classifiers, keywords, project URLs).
