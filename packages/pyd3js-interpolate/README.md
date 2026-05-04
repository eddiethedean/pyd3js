# pyd3js-interpolate

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-interpolate.svg)](https://pypi.org/project/pyd3js-interpolate/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-interpolate)](https://pypi.org/project/pyd3js-interpolate/)
[![License](https://img.shields.io/pypi/l/pyd3js-interpolate.svg)](https://pypi.org/project/pyd3js-interpolate/)

Python port of [`d3-interpolate`](https://github.com/d3/d3-interpolate).

Tracked version: [`upstream_lock.json`](../../upstream_lock.json) (`d3-interpolate@3.0.1`).

## What you get

- **Export parity** with the pinned upstream module (see [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md)).
- **100% line coverage** for `pyd3js_interpolate`.
- **Pytest ports** of the upstream Mocha tests (including `hslLong` and full `numberArray` / `value` color cases), plus an optional **upstream JS gate** (`-m upstream`).
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
- **`interpolateNumberArray`**: accepts Python `array.array`, **1-D** `memoryview`, numeric **`list` / `tuple`** (stored as `float` like JS number arrays), and **`None` as `a` or `b`** matching JS `undefined` / empty-buffer behavior; multi-dimensional or unsupported buffer formats are rejected.
- **`interpolate` / `value.js`**: `collections.abc.Mapping` (not only `dict`) uses the object interpolator; `interpolateNumber` applies a JS-style unary-`+` / `ToNumber` approximation (`valueOf` → `toString` / overridden `__str__`, with a recursion cap). Dispatch uses `ToNumber(b)` to choose object vs number, matching `value.js`. Boxed booleans via `valueOf` coerce to `0`/`1` like JS.
- **`interpolateObject`**: user-defined `valueOf` / `toString` methods on the class (not inherited from `object` alone) are included in the key set, similar to enumerable prototype fields in JS `for…in`.
- **Transforms**: `interpolateTransformSvg` parses the SVG `transform` attribute with the **same** affine composer as CSS (not only a single `matrix(...)`), including `rotate(angle cx cy)` as `translate(cx,cy) rotate(angle) translate(-cx,-cy)` and **`skewY(angle)`** (alongside `skewX`). Decomposition follows d3’s six-parameter model (`translate`, `rotate`, `skewX`, `scaleX`, `scaleY`); a lone `skewY` is folded into that basis like a browser `DOMMatrix` decomposition, not re-emitted as a `skewY(...)` token in `interpolateTransformCss` / `Svg`.
