# pyd3js-drag

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-drag.svg)](https://pypi.org/project/pyd3js-drag/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-drag)](https://pypi.org/project/pyd3js-drag/)
[![License](https://img.shields.io/pypi/l/pyd3js-drag.svg)](https://pypi.org/project/pyd3js-drag/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-drag`](https://github.com/d3/d3-drag).

Tracked version: see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

## What you get

- **100% upstream export parity** for the pinned `d3-drag@3.0.0` (see matrix below).
- **100% Python test coverage** for `pyd3js_drag`.
- **Upstream `d3-drag` JS tests vendored and passing** via a pytest gate (`-m upstream`).

## Install

From PyPI:

```bash
pip install pyd3js-drag
```

For local development (uv workspace):

```bash
uv sync --group dev
```

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-drag/docs/UPSTREAM_API.md).

Legend:

- **`[ported]`**: implemented and covered by ported upstream tests.

### Upstream exports (d3-drag@3.0.0)

- `drag` — [ported]
- `dragDisable` — [ported]
- `dragEnable` — [ported]

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-drag/package_tests
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-drag/package_tests --cov=pyd3js_drag --cov-report=term-missing
```

### Upstream `d3-drag` test suite (vendored)

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-drag/upstream/d3-drag && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-drag/package_tests
```

## Documentation

- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-drag/docs/CHANGELOG.md)
- Design notes / history: [`docs/ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-drag/docs/ROADMAP.md)
