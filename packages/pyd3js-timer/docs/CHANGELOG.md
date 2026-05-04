# Changelog

All notable changes to `pyd3js-timer` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

## 0.1.0

Initial PyPI-ready release: Python port of **`d3-timer@3.0.1`**.

### Added

- Public API: `now`, `timer` / `Timer`, `timer_flush` / `timerFlush`, `timeout`, `interval`, and `IntervalTimer`.
- Threading-based scheduler (17 ms “frame” steps and long-delay wakes) aligned with d3-timer’s `nap` / `sleep` / `wake` / `timerFlush` semantics.
- **No third-party runtime dependencies** (stdlib only); wheel bundles `LICENSE` (ISC) via Hatch metadata.
- Upstream Mocha cases ported to pytest under `package_tests/test_upstream_*.py` (Node-only `setTimeout` / `this` tests skipped with documented reasons).
- **100%** line coverage for `pyd3js_timer` enforced in `pyproject.toml` and in CI (`--cov-fail-under=100`).
- Documentation and metadata aligned with `pyd3js-array` / `pyd3js-ease`: README badges, `docs/` (user guide, changelog, upstream API/update, roadmap), `Documentation` / `Changelog` project URLs, package `.gitignore`, and hatch excludes for optional `upstream/` trees.
