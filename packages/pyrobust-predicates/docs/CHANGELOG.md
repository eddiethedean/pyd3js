# Changelog

All notable changes to **pyrobust-predicates** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.0

### Added

- Initial PyPI-ready release: Python port of **[mourner/robust-predicates@v3.0.3](https://github.com/mourner/robust-predicates/releases/tag/v3.0.3)** public API (`orient2d`, `orient3d`, `incircle`, `insphere`, plus `*fast` variants).
- **mpmath** for extended-precision `incircle` / `insphere` when the float-stage bound is inconclusive.
- Vendored upstream `test/test.js` parity suite and `.txt` fixtures under `tests/fixtures/`.
- `docs/UPSTREAM_TESTS.md` provenance and typing marker (`py.typed`).
