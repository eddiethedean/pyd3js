# pyd3js-ease

Python port of [`d3-ease`](https://github.com/d3/d3-ease).

Tracked version: [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json) (`d3-ease@3.0.1`).

## What you get

- **Export parity** with the pinned upstream module (see [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md)).
- **100% line coverage** for `pyd3js_ease` when running this package’s tests with `--cov-fail-under=100`.
- **Pytest ports** of every upstream Mocha file under `d3-ease/test/` for **v3.0.1** (`linear`, `quad`, `cubic`, `poly`, `sin`, `exp`, `circle`, `bounce`, `back`, `elastic`), including poly extra-argument parity, exponent / overshoot / amplitude·period configurators, and an export parity check against `src/index.js`.
- **D3-style `ease*` names** matching `index.js`. Polynomial, back, and elastic configurators are **classes** callable as `ease(t)` with `.exponent`, `.overshoot`, `.amplitude`, and `.period` chaining like upstream.

## Install

```bash
pip install pyd3js-ease
```

## Usage

```python
import pyd3js_ease as d3

assert d3.easeCubicIn(0.5) == 0.125
assert d3.easeQuad is d3.easeQuadInOut

# Polynomial (default exponent 3); .exponent(e) returns a new ease
p = d3.easePolyIn.exponent(2.5)
assert abs(p(0.5) - 0.176777) < 1e-5

# Elastic: .amplitude(a).period(p) chain
f = d3.easeElasticIn.amplitude(1.3).period(0.2)
assert 0.0 <= f(0.5) <= 1.0  # values match upstream tests
```

## Testing

From the package directory:

```bash
uv run pytest package_tests --cov=pyd3js_ease --cov-fail-under=100
```

## Documentation

- Changelog: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- Upstream inventory: [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md)
