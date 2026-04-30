# pyd3js-color

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-color.svg)](https://pypi.org/project/pyd3js-color/)
[![Python versions](https://badgen.net/badge/python/3.10%20|%203.11%20|%203.12/blue)](https://pypi.org/project/pyd3js-color/)
[![License: ISC](https://badgen.net/badge/license/ISC/blue)](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-color/LICENSE)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-color`](https://github.com/d3/d3-color).

Tracked version: see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

## What is d3-color?

`d3-color` implements color manipulation and parsing for CSS-like strings (`rgb`, `hsl`, hex, named colors), plus conversions among **RGB**, **HSL**, **Lab**, **HCL/LCH**, and **Cubehelix**, including formatters (`formatRgb`, `formatHex`, `formatHsl`, …).

This package mirrors that API in Python so visualization code can share the same color semantics as D3 without a JavaScript runtime.

## What you get

- **100% upstream export parity** (for the pinned `d3-color@3.1.0`): the compatibility matrix below lists every upstream export; none are marked `[missing]`.
- **100% Python test coverage** for `pyd3js_color` (run the coverage command below).
- **Upstream `d3-color` JS tests vendored** under `packages/pyd3js-color/upstream/d3-color/test/`; they are run via a pytest gate (`-m upstream`) after `npm install` in that directory.

## Install

From PyPI:

```bash
pip install pyd3js-color
```

This repo is a uv workspace monorepo. For local development:

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_color as c

red = c.color("red")
print(red.formatRgb())
print(red.rgb().brighter(0.5).formatHex())

print(c.hsl(120, 0.5, 0.5).formatHsl())
print(c.lab(50, 10, -20).formatRgb())
print(c.cubehelix(300, 0.5, 0.5).formatRgb())
```

```text
rgb(255, 0, 0)
#ff4040
hsl(120, 50%, 50%)
rgb(137, 117, 211)
rgb(142, 93, 166)
```

## Stability & intentional deviations

- **Signed zero / JS float trivia**: behavior matches D3 where tests require it; any residual float differences are covered in unit tests (oracle payloads stay JSON-safe).
- **Oracle parity limits**: optional oracle tests compare JSON-safe strings and numbers only (`NaN` / `-0` are exercised in Python tests instead).

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-color/docs/UPSTREAM_API.md) (from `d3-color@3.1.0`).

Legend:

- **`[oracle]`**: implemented with optional oracle parity for representative JSON-safe cases (string/numeric outputs).
- **`[unit-only: …]`**: implemented; oracle coverage is limited by JSON or by API shape.
- **`[missing]`**: reserved for upstream drift (should not appear for the pinned version).

### Upstream exports (d3-color@3.1.0)

- `color` — [oracle]
- `cubehelix` — [oracle]
- `gray` — [oracle]
- `hcl` — [oracle]
- `hsl` — [oracle]
- `lab` — [oracle]
- `lch` — [oracle]
- `rgb` — [oracle]

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-color/package_tests
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-color/package_tests --cov=pyd3js_color --cov-report=term-missing
```

### Oracle parity tests (Node)

Some tests compare behavior against real `d3` (includes `d3-color`) via the repo’s Node oracle:

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-color/package_tests
```

Notes:

- Oracle tests must use **JSON-safe** values where practical (avoid ambiguous `-0` / `NaN` in payloads).
- You can optionally enable local oracle caching by creating `packages/pyd3js-color/.env` with:
  - `ORACLE_CACHE=1`
  (do not commit it).

### Upstream `d3-color` test suite (vendored)

We vendor the pinned upstream `d3-color` repo (including its Mocha test suite) and run it via pytest.

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-color/upstream/d3-color && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-color/package_tests
```

## Documentation

- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-color/docs/CHANGELOG.md)
- Upstream export inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-color/docs/UPSTREAM_API.md)
- Updating upstream: [`docs/UPSTREAM_UPDATE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-color/docs/UPSTREAM_UPDATE.md)
