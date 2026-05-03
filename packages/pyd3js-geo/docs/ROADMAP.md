# pyd3js-geo roadmap

This package is a Python port of [`d3-geo`](https://github.com/d3/d3-geo) with the goal of **matching the upstream public API** and **numerical / behavioral parity** for mapping and spherical geometry workflows.

Tracked upstream version is pinned at the repo level in `upstream_lock.json` (`d3-geo@3.1.1`).

## Guiding principles

- **API parity**: exports listed in `docs/UPSTREAM_API.md` map to `pyd3js_geo.__all__` (plus `__version__`).
- **Test-backed changes**: default CI runs smoke tests and doc examples; full ported JS suite is opt-in until every case matches.
- **Pythonic usage**: GeoJSON-shaped objects, type hints where practical; internal code may mirror JS structure for port fidelity.

## Current status

- **Exports**: all symbols from upstream `index.js` are implemented and exported (see README compatibility matrix).
- **Default tests**: `package_tests/test_geo_smoke.py`, `test_geo_docs_examples.py`, and parity-matrix checks run in normal CI.
- **Upstream JS tests**: `package_tests/test_upstream_*.py` mirror `d3-geo` tests; they are **skipped unless** `PYD3JS_GEO_FULL_UPSTREAM=1`.
- **Known gaps** (tracked via skips / notes in upstream tests):
  - **Albers / Albers USA**: some forward / `fit*` cases vs d3 fixtures still pending full parity.
  - **Canvas PNG snapshots** from upstream are not ported (browser-specific).
  - **Internal `polygonContains`** parity test remains skipped where behavior is still being aligned.

## Next steps

- Close Albers USA composite + regional clip parity for `fitExtent` / `fitWidth` / `fitHeight` and forward sampling vs d3.
- Tighten tolerances on projection fit tests once parity is stable.
- Optionally add coverage gates (`pytest-cov`) per package similar to `pyd3js-array` once line coverage is tracked consistently.
