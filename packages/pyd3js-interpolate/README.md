# pyd3js-interpolate

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-interpolate.svg)](https://pypi.org/project/pyd3js-interpolate/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-interpolate)](https://pypi.org/project/pyd3js-interpolate/)
[![License](https://img.shields.io/pypi/l/pyd3js-interpolate.svg)](https://pypi.org/project/pyd3js-interpolate/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-interpolate`](https://github.com/d3/d3-interpolate).

Tracked version: [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json) (`d3-interpolate@3.0.1`).

## What is d3-interpolate?

`d3-interpolate` provides **interpolators**: functions that map a parameter \(t \in [0,1]\) between two values (numbers, colors, dates, arrays, affine transforms, zoom views, and more). D3 uses these for transitions and animations; this package brings the same building blocks to Python (with **DOM-free** transform parsing).

## What you get

- **100% upstream export parity** for the pinned `d3-interpolate@3.0.1` (see the compatibility matrix and [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md)).
- **100% line coverage** for `pyd3js_interpolate` (enforced via `--cov-fail-under=100` when running this package’s tests).
- **Pytest ports** of the upstream Mocha tests, plus an optional **vendored Mocha gate** (`-m upstream`) after `scripts/vendor_upstream.py` and `npm install`.
- **Runnable docs**: [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) examples are checked by the test suite (same pattern as `pyd3js-array`).
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
print(i(0.5))

c = d3.interpolateRgb("steelblue", "brown")
print(c(0.5))
```

```text
5.0
rgb(118, 86, 111)
```

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-interpolate/docs/UPSTREAM_API.md).

Legend:

- **`[implemented]`**: ported for the pinned version; covered by Python tests (and optional upstream Mocha gate).
- **`[missing]`**: reserved for upstream drift (should not appear for the pinned version).

### Upstream exports (`d3-interpolate@3.0.1`)

- `interpolate` — [implemented]
- `interpolateArray` — [implemented]
- `interpolateBasis` — [implemented]
- `interpolateBasisClosed` — [implemented]
- `interpolateDate` — [implemented]
- `interpolateDiscrete` — [implemented]
- `interpolateHue` — [implemented]
- `interpolateNumber` — [implemented]
- `interpolateNumberArray` — [implemented]
- `interpolateObject` — [implemented]
- `interpolateRound` — [implemented]
- `interpolateString` — [implemented]
- `interpolateTransformCss` — [implemented]
- `interpolateTransformSvg` — [implemented]
- `interpolateZoom` — [implemented]
- `interpolateRgb` — [implemented]
- `interpolateRgbBasis` — [implemented]
- `interpolateRgbBasisClosed` — [implemented]
- `interpolateHsl` — [implemented]
- `interpolateHslLong` — [implemented]
- `interpolateLab` — [implemented]
- `interpolateHcl` — [implemented]
- `interpolateHclLong` — [implemented]
- `interpolateCubehelix` — [implemented]
- `interpolateCubehelixLong` — [implemented]
- `piecewise` — [implemented]
- `quantize` — [implemented]

### Python-only helpers

The module also exposes **`isNumberArray`** / **`is_number_array`**, snake_case **`interpolate_*`** aliases, **`interpolate_value`**, **`generic_array`**, and **`basis_fn`** for Python ergonomics (not separate names in upstream `index.js`).

## Testing

```bash
# From repo root, or from this package directory (`uv run pytest` enforces 100% line coverage via pyproject.toml):
uv run pytest packages/pyd3js-interpolate/package_tests --cov=pyd3js_interpolate --cov-fail-under=100
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

Use `npm install --legacy-peer-deps` if the vendored tree requires it (same as `pyd3js-array`).

## Documentation

- User guide: [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)
- Changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Roadmap: [`docs/ROADMAP.md`](docs/ROADMAP.md)
- Upstream update checklist: [`docs/UPSTREAM_UPDATE.md`](docs/UPSTREAM_UPDATE.md)

## Stability notes

- **Numbers / truthiness**: interpolators treat IEEE NaN like JavaScript (e.g. `nogamma` uses a JS-style “truthy difference” check).
- **`interpolateNumberArray`**: accepts Python `array.array`, **1-D** `memoryview`, numeric **`list` / `tuple`** (stored as `float` like JS number arrays), and **`None` as `a` or `b`** matching JS `undefined` / empty-buffer behavior; multi-dimensional or unsupported buffer formats are rejected.
- **`interpolate` / `value.js`**: `collections.abc.Mapping` (not only `dict`) uses the object interpolator; `interpolateNumber` applies a JS-style unary-`+` / `ToNumber` approximation (`valueOf` → `toString` / overridden `__str__`, with a recursion cap). Dispatch uses `ToNumber(b)` to choose object vs number, matching `value.js`. Boxed booleans via `valueOf` coerce to `0`/`1` like JS.
- **`interpolateObject`**: user-defined `valueOf` / `toString` methods on the class (not inherited from `object` alone) are included in the key set, similar to enumerable prototype fields in JS `for…in`.
- **Transforms**: `interpolateTransformSvg` parses the SVG `transform` attribute with the **same** affine composer as CSS (not only a single `matrix(...)`), including `rotate(angle cx cy)` as `translate(cx,cy) rotate(angle) translate(-cx,-cy)` and **`skewY(angle)`** (alongside `skewX`). Decomposition follows d3’s six-parameter model (`translate`, `rotate`, `skewX`, `scaleX`, `scaleY`); a lone `skewY` is folded into that basis like a browser `DOMMatrix` decomposition, not re-emitted as a `skewY(...)` token in `interpolateTransformCss` / `Svg`.
