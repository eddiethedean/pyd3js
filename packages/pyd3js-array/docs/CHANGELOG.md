# Changelog

All notable changes to `pyd3js-array` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.1

### Changed

- Documentation and CI hardening:
  - Consolidated package docs under `packages/pyd3js-array/docs/`.
  - Updated examples to use `import pyd3js_array as ar` to avoid shadowing Python built-ins.
  - Security workflow dependency review is non-blocking when GitHub Dependency Graph is disabled.
  - CI runs tests concurrently (`pytest -n 10`).

## 0.1.0

### Added

- Completed parity for all remaining `d3-array@3.2.4` exports:
  - Iterables/utilities: `map`, `filter`, `reduce`, `reverse`, `merge`, `every`, `some`
  - Index helpers: `minIndex`, `maxIndex`, `medianIndex`, `quantileIndex`, `mode`, and `bisect` alias
  - Numeric helpers: `count`, `cumsum`, `fsum`, `fcumsum`, and `Adder`
  - Threshold helpers: `thresholdFreedmanDiaconis`, `thresholdScott`, `thresholdSturges`
  - Grouping helpers: `flatGroup`, `flatRollup`
  - Interning helpers: `InternMap`, `InternSet`
  - Blur helpers: `blur`, `blur2`, `blurImage`
- Vendored upstream `d3-array` Mocha suite gate (`pytest -m upstream`) and expanded parity/coverage tests.
- Phase 2 utilities: `ticks`, `tickIncrement`, `tickStep`, `nice`, `bisectLeft`, `bisectRight`,
  `bisectCenter`, `bisector`, `bin` / `histogram`, `ascending`, `descending`, `shuffle`.
- Phase 5 grouping and set helpers: `group`, `groups`, `index`, `indexes`, `rollup`, `rollups`,
  `union`, `intersection`, `difference`, `superset`, `subset`, `disjoint`.
- Phase 6 sorting and selection helpers: `sort`, `groupSort`, `rank`, `permute`, `quickselect`.
- Phase 7 sequence helpers: `cross`, `pairs`, `zip`, `transpose`, `scan`.
- Phase 8 random helpers: `shuffler` (seedable shuffle factory).
- Docs and DX improvements:
  - Compatibility matrix and expanded usage examples in `README.md`.
  - Improved upstream/oracle testing instructions.
- Added lightweight micro-benchmark harness at `packages/pyd3js-array/tools/bench/bench.py`.

### Changed

- Optimized numeric reducer iteration (`_iter.iter_observed_numbers`) with primitive fast paths.
- Tightened typing across reducers, ordering helpers, and sort/bisector APIs.

### Packaging

- Added `py.typed` marker and package metadata suitable for PyPI.

## 0.0.1

- Added oracle parity tests for `extent`, `min`, `max`, and `range`.
- Expanded `extent` edge-case coverage (infinities, accessor filtering).

