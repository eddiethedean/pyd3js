# pyd3js-interpolate

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-interpolate.svg)](https://pypi.org/project/pyd3js-interpolate/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-interpolate)](https://pypi.org/project/pyd3js-interpolate/)
[![License](https://img.shields.io/pypi/l/pyd3js-interpolate.svg)](https://pypi.org/project/pyd3js-interpolate/)

Python port of [`d3-interpolate`](https://github.com/d3/d3-interpolate).

Tracked version: [`upstream_lock.json`](../../upstream_lock.json) (`d3-interpolate@3.0.1`).

## What you get

- **Export parity** with the pinned upstream module (see [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md)).
- **100% line coverage** for `pyd3js_interpolate`.
- **Pytest ports** of the upstream Mocha tests, plus an optional **upstream JS gate** (`-m upstream`).
- **D3-style camelCase** names on the package (e.g. `interpolateRgb`) and **snake_case** equivalents (e.g. `interpolate_rgb`).
- **DOM-free** `interpolateTransformCss` / `interpolateTransformSvg` (no browser `DOMMatrix` or SVG DOM).

## Install

```bash
pip install pyd3js-interpolate
```

Workspace development:

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_interpolate as d3

i = d3.interpolate(0, 10)
assert i(0.5) == 5

c = d3.interpolateRgb("steelblue", "brown")
assert "rgb(" in c(0.5)
```

## Compatibility matrix

Pinned inventory: [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md).

## Testing

```bash
uv run pytest packages/pyd3js-interpolate/package_tests
uv run pytest packages/pyd3js-interpolate/package_tests --cov=pyd3js_interpolate --cov-report=term-missing
uv run ruff format packages/pyd3js-interpolate
uv run ruff check packages/pyd3js-interpolate
uv run ty check packages/pyd3js-interpolate/src
```

### Upstream Mocha suite (optional)

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-interpolate/upstream/d3-interpolate && npm install
uv run pytest -m upstream packages/pyd3js-interpolate/package_tests
```

## Documentation

- Changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Roadmap: [`docs/ROADMAP.md`](docs/ROADMAP.md)
- Upstream update checklist: [`docs/UPSTREAM_UPDATE.md`](docs/UPSTREAM_UPDATE.md)

## Stability notes

- **Numbers / truthiness**: interpolators treat IEEE NaN like JavaScript (e.g. `nogamma` uses a JS-style “truthy difference” check).
- **`interpolateNumberArray`**: maps to Python `array.array` for typed numeric buffers (see `is_number_array` / `isNumberArray`).
- **Transforms**: CSS parsing supports common `transform` functions via a small matrix composer; it is not a full browser `DOMMatrix` implementation.
