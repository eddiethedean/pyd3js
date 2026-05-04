# pyd3js-ease

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-ease.svg)](https://pypi.org/project/pyd3js-ease/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-ease)](https://pypi.org/project/pyd3js-ease/)
[![License](https://img.shields.io/pypi/l/pyd3js-ease.svg)](https://pypi.org/project/pyd3js-ease/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-ease`](https://github.com/d3/d3-ease).

Tracked version: [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json) (`d3-ease@3.0.1`).

## What is d3-ease?

`d3-ease` supplies **easing functions**: maps \(t \in [0,1]\) for animations and transitions (polynomial, sinusoidal, exponential, elastic, bounce, etc.). This package mirrors the **default export surface** of the pinned upstream version for use from Python.

## What you get

- **100% upstream export parity** for the pinned `d3-ease@3.0.1` (compatibility matrix and [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md)).
- **100% line coverage** for `pyd3js_ease` (enforced via `--cov-fail-under=100` in this package’s pytest config).
- **Pytest ports** of every upstream Mocha file for v3.0.1, plus **runnable docs** (README + [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)) checked like `pyd3js-array`.
- **D3-style `ease*` names** and aliases; polynomial, back, and elastic configurators expose **`.exponent`**, **`.overshoot`**, **`.amplitude` / `.period`** like upstream (as callable classes in Python).

## Install

From PyPI:

```bash
pip install pyd3js-ease
```

Workspace development:

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_ease as d3

print(d3.easeCubicIn(0.5))
print(d3.easeQuad is d3.easeQuadInOut)

p = d3.easePolyIn.exponent(2.5)
print(round(p(0.5), 6))

f = d3.easeElasticIn.amplitude(1.3).period(0.2)
print(round(f(0.5), 6))
```

```text
0.125
True
0.176777
-0.030303
```

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-ease/docs/UPSTREAM_API.md).

Legend:

- **`[implemented]`**: ported for the pinned version; covered by Python tests.
- **`[missing]`**: reserved for upstream drift (should not appear for the pinned version).

### Upstream exports (`d3-ease@3.0.1`)

- `easeLinear` — [implemented]
- `easeQuad` — [implemented]
- `easeQuadIn` — [implemented]
- `easeQuadOut` — [implemented]
- `easeQuadInOut` — [implemented]
- `easeCubic` — [implemented]
- `easeCubicIn` — [implemented]
- `easeCubicOut` — [implemented]
- `easeCubicInOut` — [implemented]
- `easePoly` — [implemented]
- `easePolyIn` — [implemented]
- `easePolyOut` — [implemented]
- `easePolyInOut` — [implemented]
- `easeSin` — [implemented]
- `easeSinIn` — [implemented]
- `easeSinOut` — [implemented]
- `easeSinInOut` — [implemented]
- `easeExp` — [implemented]
- `easeExpIn` — [implemented]
- `easeExpOut` — [implemented]
- `easeExpInOut` — [implemented]
- `easeCircle` — [implemented]
- `easeCircleIn` — [implemented]
- `easeCircleOut` — [implemented]
- `easeCircleInOut` — [implemented]
- `easeBounce` — [implemented]
- `easeBounceIn` — [implemented]
- `easeBounceOut` — [implemented]
- `easeBounceInOut` — [implemented]
- `easeBack` — [implemented]
- `easeBackIn` — [implemented]
- `easeBackOut` — [implemented]
- `easeBackInOut` — [implemented]
- `easeElastic` — [implemented]
- `easeElasticIn` — [implemented]
- `easeElasticOut` — [implemented]
- `easeElasticInOut` — [implemented]

### Python-only exports

The module also documents **`PolyIn`**, **`PolyOut`**, **`PolyInOut`**, **`BackIn`**, **`BackOut`**, **`BackInOut`**, **`ElasticIn`**, **`ElasticOut`**, **`ElasticInOut`**, and **`__version__`** for typing and explicit construction (not separate names in upstream `index.js`).

## Testing

From repo root:

```bash
uv run pytest packages/pyd3js-ease/package_tests -q --cov=pyd3js_ease --cov-report=term-missing --cov-fail-under=100
```

```bash
uv run ruff format packages/pyd3js-ease
uv run ruff check packages/pyd3js-ease
uv run ty check packages/pyd3js-ease/src
```

## Documentation

- User guide: [`docs/USER_GUIDE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-ease/docs/USER_GUIDE.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-ease/docs/CHANGELOG.md)
- Roadmap: [`docs/ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-ease/docs/ROADMAP.md)
- Upstream update checklist: [`docs/UPSTREAM_UPDATE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-ease/docs/UPSTREAM_UPDATE.md)
