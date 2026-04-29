# pyd3js-array roadmap

This package is a Python port of [`d3-array`](https://github.com/d3/d3-array) with a strong focus on **behavioral parity** (especially around JavaScript-ish comparison / coercion edge cases) and **good Python ergonomics**.

Tracked upstream version is pinned at the repo level in `upstream_lock.json`.

## Guiding principles

- **Parity first**: match `d3-array` observable behavior (including tricky cases like `None`/`NaN`, mixed types, and accessors).
- **Small, testable increments**: each exported function lands with focused unit tests, plus oracle parity tests where feasible.
- **Pythonic surface without surprises**: keep names and defaults aligned with D3, but offer type hints and docstrings that make sense in Python.

## Current status (today)

- **Implemented (Phase 0 + Phase 1)**:
  - Core: `extent`, `min`, `max`, `range`
  - Reducers/statistics: `sum`, `mean`, `median`, `quantile`, `quantileSorted`, `variance`, `deviation`
  - Extrema helpers: `least`, `greatest`, `leastIndex`, `greatestIndex`
- **Tests**:
  - Unit tests for all public APIs
  - Oracle parity tests (`@pytest.mark.oracle`) for representative cases
  - `pyd3js_array` maintains **100% line coverage**
- **Core helpers**:
  - `_compare.py` provides JS-ish coercion and relational comparisons
  - `_iter.py` centralizes D3-style filtering/accessor + numeric coercion semantics
  - `_ordering.py` provides a default comparator for `least/greatest`
- **CI**: GitHub Actions runs pytest and installs the Node oracle so oracle-marked tests execute in CI

## Roadmap phases

### Phase 0 — solidify the existing surface (patch releases)

- **Status**: complete
- **Correctness parity**
  - Oracle parity tests added for: `extent`, `min`, `max`, `range`
  - Expanded edge-case coverage (including accessor behavior)
- **Typing/docs**
  - Type hints + docstrings upgraded across public API
- **Release hygiene**
  - `CHANGELOG.md` added and maintained
  - Release artifacts validated via `build` + `twine check`

Acceptance criteria:
- All existing exported functions have oracle parity tests and pass.

### Phase 1 — “reducers” and basic statistics (minor releases)

Implement the most commonly-used statistical helpers first.

- **Reducers**
  - `sum(values, valueof=None)` (implemented)
  - `mean(values, valueof=None)` (implemented)
  - `median(values, valueof=None)` (implemented)
  - `quantile(values, p, valueof=None)` (implemented)
  - `quantileSorted(values, p, valueof=None)` (implemented)
- **Dispersion**
  - `variance(values, valueof=None)` (implemented)
  - `deviation(values, valueof=None)` (implemented)
- **Extrema helpers**
  - `least(values, compare=None)` / `greatest(values, compare=None)` (implemented)
  - `leastIndex(values, compare=None)` / `greatestIndex(values, compare=None)` (implemented)

Acceptance criteria:
- Each function has:
  - unit tests covering null/NaN filtering and accessors
  - oracle parity tests for representative cases

### Phase 2 — binning, searching, ordering utilities (minor releases)

- **Binning**
  - `ticks(start, stop, count)`
  - `tickIncrement(start, stop, count)`
  - `tickStep(start, stop, count)`
  - `nice(start, stop, count)` (or equivalent if upstream exposes it here)
  - `histogram()` / `bin()` API parity (including thresholds, domain, and value accessors)
- **Searching**
  - `bisectLeft`, `bisectRight`, `bisectCenter` (and `bisector` factory)
- **Ordering / permuting**
  - `ascending(a, b)`, `descending(a, b)` comparators (if needed publicly)
  - `shuffle(array, start=0, stop=None)` (pay attention to determinism/testing)

Acceptance criteria:
- `bin/histogram` matches D3 for:
  - default thresholds
  - clamping to domain
  - inclusive/exclusive boundaries

### Phase 3 — polish + performance + stability (1.0 prep)

- **API stability**
  - finalize naming decisions where Python keywords conflict (e.g. `range_` internally vs exported `range`)
  - document any intentional deviations from D3 (if any)
- **Performance**
  - micro-optimize hot paths (reducers on large lists)
  - consider optional fast paths for homogeneous numeric input
- **DX improvements**
  - add “How to test against upstream” doc snippet
  - add small usage examples for each public function

Acceptance criteria:
- A “compatibility matrix” section (implemented vs planned) is complete and accurate.
- CI runs oracle tests in at least one job (if Node is available in CI).

### Phase 4 — parity audit + compatibility matrix (toward “100% parity”)

Goal: define what “100% parity” means and measure it precisely.

- **Upstream API inventory**
  - Generate a canonical list of exported functions from the pinned upstream `d3-array` version.
  - Record this list in-repo (e.g. `packages/pyd3js-array/UPSTREAM_API.md`) so parity can be tracked over time.
- **Compatibility matrix (full)**
  - Expand the compatibility matrix to enumerate *every* upstream export and mark:
    - implemented + oracle parity
    - implemented + unit-only (oracle blocked by JSON limitations or nondeterminism)
    - missing
  - For “unit-only” items, explicitly document the reason (e.g. `Infinity` / `-0` / `NaN` JSON round-trip, RNG).
- **Parity gates**
  - Add a small test or check that fails CI if the matrix references unknown exports or goes out of sync with the Python public API.

Acceptance criteria:
- A complete upstream export inventory exists for the pinned version.
- The compatibility matrix covers 100% of upstream exports and is kept in sync.

### Phase 5 — grouping + sets + indexing helpers (missing core surface area)

Implement common `d3-array` helpers that are widely used for data prep:

- **Grouping / indexing**
  - `group`, `groups`
  - `index`, `indexes`
  - `rollup`, `rollups`
- **Sets**
  - `union`, `intersection`, `difference`, `superset`, `subset`, `disjoint`

Testing:
- Unit tests for accessors and nested key semantics.
- Oracle parity tests for representative JSON-safe cases.

Acceptance criteria:
- All Phase 5 APIs exported, documented, and have oracle parity where deterministic/JSON-safe.

### Phase 6 — sorting, ranking, and selection utilities

Implement the ordering and selection surface area beyond comparators:

- **Sorting / ranking**
  - `sort`, `groupSort`
  - `rank`
  - `permute`
- **Selection**
  - `quickselect`

Testing:
- Property tests (permutation/invariants) for selection algorithms.
- Oracle parity for deterministic behaviors and JSON-safe inputs.

Acceptance criteria:
- Deterministic selection/sort semantics match upstream for representative cases.

### Phase 7 — sequences, scans, and iterator-style helpers

Implement the “array plumbing” utilities commonly used in pipelines:

- `cross`
- `pairs`
- `zip`
- `transpose`
- `ticks`-adjacent helpers if any remain upstream-exposed (already implemented: `ticks`, `tickStep`, `tickIncrement`, `nice`)
- `scan` (and any related helpers upstream exposes)

Testing:
- Oracle parity for deterministic JSON-safe cases.
- Unit tests for edge cases (empty inputs, ragged arrays, accessor behavior).

Acceptance criteria:
- All Phase 7 APIs exported and parity-tested.

### Phase 8 — random sampling + distributions (parity with explicit RNG story)

Implement random-related utilities with a clear parity strategy:

- `shuffle` is already implemented; add remaining random helpers if upstream exports them (e.g. sampling APIs).
- Define a consistent approach for testing randomness:
  - invariant/property tests for core correctness
  - optional seeded RNG injection for deterministic parity checks (if feasible without changing the public API)

Acceptance criteria:
- Random APIs have strong invariant-based tests; any deterministic parity approach is documented.

### Phase 9 — “100% parity” hardening + upstream drift management

- **Expand oracle coverage**
  - For each implemented function, increase oracle case coverage to include tricky-but-JSON-safe inputs.
- **Converted upstream tests (optional)**
  - Continue converting upstream test suites where it adds value, but keep oracle parity as primary signal.
- **Upstream drift**
  - Document a process for updating `upstream_lock.json` and re-validating parity.

Acceptance criteria:
- Every upstream export is either implemented with parity tests or explicitly documented as not applicable/blocked (with rationale).
- “100% parity” claim is backed by an auditable compatibility matrix + CI checks.

## Testing strategy (recommended)

- **Unit tests**: keep fast, deterministic, cover Python edge cases.
- **Oracle parity tests** (`@pytest.mark.oracle`): for behavior that is easiest to verify by comparing to real `d3-array` in Node via `tools/oracle`.
- **Converted upstream tests**: optionally continue building out the `tape_to_pytest` conversion flow, but treat oracle + focused unit tests as the primary correctness signal.

## Contribution checklist (per new function)

- Add function implementation under `src/pyd3js_array/`.
- Export from `src/pyd3js_array/__init__.py`.
- Add pytest tests in `tests/`.
- Add at least one oracle parity test (when the function exists in `d3-array` and is deterministic).
- Document the function briefly (docstring + a short README/roadmap update).

