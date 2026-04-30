# Changelog

All notable changes to `pyd3js-color` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.0

### Added

- Initial release: Python port of **`d3-color@3.1.0`** with public API `color`, `rgb`, `hsl`,
  `lab`, `gray`, `hcl`, `lch`, and `cubehelix`.
- Parity documentation (`docs/UPSTREAM_API.md`), README compatibility matrix, and parity-gate tests.
- Unit tests from upstream Mocha scenarios; optional Node oracle smoke tests; `-m upstream` gate for the vendored upstream suite (requires local vendor + `npm install`).
- ISC license; type hints (`py.typed`).
