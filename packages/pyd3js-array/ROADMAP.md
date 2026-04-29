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

