# pyd3js-delaunay roadmap

Python port of [`d3-delaunay`](https://github.com/d3/d3-delaunay) focused on **observable parity** with the pinned upstream release and **zero Node.js** in tests or runtime.

Tracked upstream: **`d3-delaunay@6.0.4`** (`upstream_lock.json` at repo root).

## Guiding principles

- **Parity first**: match upstream behavior for the public `Delaunay` / `Voronoi` API (including degeneracies: few points, collinear input, clipping).
- **Pure Python tests**: upstream Mocha cases live as pytest ports in `package_tests/`, not as an `npm test` subprocess.
- **Ergonomic Python surface**: snake_case methods, typed public API, `py.typed`, and selective **camelCase aliases** on `Voronoi` where d3 uses them.

## Current status

- **Exports**: `Delaunay`, `Voronoi`, and `__version__` — parity-checked against `docs/UPSTREAM_API.md` and `README.md` (`test_parity_matrix.py`).
- **Implementation**: triangulation via **[dylaunator](https://pypi.org/project/dylaunator/)**; robust predicates via **[pyrobust-predicates](https://pypi.org/project/pyrobust-predicates/)** (same role as upstream `robust-predicates`).
- **Tests**: unit and branch tests in `package_tests/` plus full ports of upstream `test/delaunay-test.js` and `test/voronoi-test.js`.
- **Docs**: README, user guide (`docs/USER_GUIDE.md`), upstream inventory, changelog — example snippets are executed in CI via `test_delaunay_docs_examples.py`.

## Near-term

- Keep the pin on **6.0.4** until a deliberate upstream bump; then follow [`UPSTREAM_UPDATE.md`](UPSTREAM_UPDATE.md).
- Optionally raise line coverage toward **100%** for `pyd3js_delaunay` using targeted branch tests (similar discipline to `pyd3js-array`).
