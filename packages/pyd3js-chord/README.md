# pyd3js-chord

Python port of [`d3-chord`](https://github.com/d3/d3-chord).

Tracked version: see [upstream_lock.json](../../upstream_lock.json).

## What you get

- **100% upstream export parity** (for the pinned `d3-chord@3.0.1`): the compatibility matrix below covers every upstream export.
- **100% Python test coverage** for `pyd3js_chord` (run the coverage command below).
- **100% upstream `d3-chord` JS tests vendored and passing**: the upstream Mocha suite under `packages/pyd3js-chord/upstream/d3-chord/test/` is run via a pytest gate (`-m upstream`).
- **Oracle parity checks (where feasible)**: representative tests compare results to upstream via the repo’s Node oracle (`-m oracle`).

## Install

From PyPI:

```bash
pip install pyd3js-chord
```

This repo is a uv workspace monorepo. For local development:

```bash
uv sync --group dev
```

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md) (from `d3-chord@3.0.1`).

Legend:

- **`[oracle]`**: implemented and has oracle parity tests for representative cases.
- **`[unit + upstream-js]`**: implemented and covered by Python unit tests plus the vendored upstream JS suite gate.

### Upstream exports (d3-chord@3.0.1)

- `chord` — [oracle]
- `chordTranspose` — [oracle]
- `chordDirected` — [oracle]
- `ribbon` — [oracle]
- `ribbonArrow` — [oracle]

## Development

```bash
uv run pytest packages/pyd3js-chord/package_tests
uv run ruff format packages/pyd3js-chord
uv run ruff check packages/pyd3js-chord
uv run ty check packages/pyd3js-chord/src
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-chord/package_tests --cov=pyd3js_chord --cov-report=term-missing
```

### Oracle parity tests (Node)

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-chord/package_tests
```

### Upstream `d3-chord` test suite (vendored)

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-chord/upstream/d3-chord && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-chord/package_tests
```

## Documentation

- Upstream export inventory: `docs/UPSTREAM_API.md`
