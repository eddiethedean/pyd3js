# pyd3js-selection

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-selection.svg)](https://pypi.org/project/pyd3js-selection/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-selection)](https://pypi.org/project/pyd3js-selection/)
[![License](https://img.shields.io/pypi/l/pyd3js-selection.svg)](https://pypi.org/project/pyd3js-selection/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-selection`](https://github.com/d3/d3-selection).

Tracked version: see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

## What you get

- **100% upstream export parity** for the pinned `d3-selection@3.0.0` (see matrix below).
- **100% Python test coverage** for `pyd3js_selection`.
- **Upstream `d3-selection` JS tests vendored and passing** via a pytest gate (`-m upstream`).

## Install

From PyPI:

```bash
pip install pyd3js-selection
```

For local development (uv workspace):

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_selection as d3

root = d3.create("div")
root.append("span").text("hi")

print(root.node().innerHTML)
```

```text
<span>hi</span>
```

## Stability & intentional deviations

- **Minimal DOM**: this package includes a tiny DOM shim sufficient for upstream `d3-selection` semantics and tests; it is not a full browser DOM implementation.
- **Callback “this”**: D3’s `this` binding is represented explicitly (callbacks receive `this` as their first argument).

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-selection/docs/UPSTREAM_API.md).

Legend:

- **`[ported]`**: implemented and covered by ported upstream tests.
- **`[missing]`**: reserved for future upstream drift.

### Upstream exports (d3-selection@3.0.0)

- `create` — [ported]
- `creator` — [ported]
- `local` — [ported]
- `matcher` — [ported]
- `namespace` — [ported]
- `namespaces` — [ported]
- `pointer` — [ported]
- `pointers` — [ported]
- `select` — [ported]
- `selectAll` — [ported]
- `selection` — [ported]
- `selector` — [ported]
- `selectorAll` — [ported]
- `style` — [ported]
- `window` — [ported]

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-selection/package_tests
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-selection/package_tests --cov=pyd3js_selection --cov-report=term-missing
```

### Upstream `d3-selection` test suite (vendored)

We vendor the pinned upstream `d3-selection` repo (including its Mocha test suite) and run it via pytest:

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-selection/upstream/d3-selection && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-selection/package_tests
```

## Documentation

- User guide: [`docs/USER_GUIDE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-selection/docs/USER_GUIDE.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-selection/docs/CHANGELOG.md)
