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
- **Upstream JS tests**: `package_tests/test_upstream_*.py` mirror `d3-geo` tests; they are **skipped unless** `PYD3JS_GEO_FULL_UPSTREAM=1`, where full parity and **100% line coverage** on `pyd3js_geo` are asserted for supported workflows.
- **Known gaps**:
  - **Canvas PNG snapshots** from upstream are not ported (browser-specific); path-context equivalence is tested in Python instead.

## Next steps

- Keep upstream pins (`upstream_lock.json`) aligned when bumping `d3-geo`.
- Tolerances on projection fit tests can be tightened further if future upstream fixtures narrow expected deltas.
- Extend narrative docs under `docs/guides/` as workflows emerge beyond core parity.
