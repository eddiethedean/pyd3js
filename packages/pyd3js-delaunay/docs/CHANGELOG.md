# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-02

### Added

- Initial published release: `Delaunay` and `Voronoi` ports aligned with **d3-delaunay@6.0.4**.
- Pure-Python upstream parity tests (Mocha `test/delaunay-test.js` and `test/voronoi-test.js` ported to pytest under `package_tests/`).
- `py.typed` marker and packaging metadata (`project.urls`, `license` file, sdist includes).
- User guide, roadmap, upstream update notes, and README examples checked in CI (`test_delaunay_docs_examples.py`).

### Changed

- Runtime triangulation via **[dylaunator](https://pypi.org/project/dylaunator/)** **==0.1.0** (no Node.js / npm).

[0.1.0]: https://github.com/eddiethedean/pyd3js/tree/main/packages/pyd3js-delaunay
