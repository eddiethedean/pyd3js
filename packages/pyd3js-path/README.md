# pyd3js-path

Python port of [`d3-path`](https://github.com/d3/d3-path).

Tracked version: see [upstream_lock.json](../../upstream_lock.json).

## What you get

- **100% upstream export parity** (for the pinned `d3-path@3.1.0`): the compatibility matrix below covers every upstream export.
- **100% Python test coverage** for `pyd3js_path` (run the coverage command below).
- **100% upstream `d3-path` JS tests vendored and passing**: the upstream Mocha suite under `packages/pyd3js-path/upstream/d3-path/test/` is run via a pytest gate (`-m upstream`).
- **UI parity checks (oracle)**: representative tests compare the SVG path `d` output to upstream via the repo’s Node oracle (`-m oracle`).

## Install

From PyPI:

```bash
pip install pyd3js-path
```

This repo is a uv workspace monorepo. For local development:

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_path as p

path = p.path()
path.moveTo(0, 0)
path.lineTo(10, 10)
print(str(path))
```

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md) (from `d3-path@3.1.0`).

Legend:

- **`[oracle]`**: implemented and has oracle parity tests for representative cases.
- **`[unit + upstream-js]`**: implemented and covered by Python unit tests plus the vendored upstream JS suite gate.

### Upstream exports (d3-path@3.1.0)

- `Path` — [oracle]
- `path` — [oracle]
- `pathRound` — [oracle]

## Development

```bash
uv run pytest packages/pyd3js-path/package_tests
uv run ruff format packages/pyd3js-path
uv run ruff check packages/pyd3js-path
uv run ty check packages/pyd3js-path/src
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-path/package_tests --cov=pyd3js_path --cov-report=term-missing
```

### Oracle parity tests (Node)

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-path/package_tests
```

### Upstream `d3-path` test suite (vendored)

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-path/upstream/d3-path && npm install
uv run pytest -m upstream packages/pyd3js-path/package_tests
```

## Documentation

- Upstream export inventory: `docs/UPSTREAM_API.md`
