# pyd3js-contour

Python port of [`d3-contour`](https://github.com/d3/d3-contour).

Tracked version: see [`upstream_lock.json`](../../upstream_lock.json).

## Public API

Matches **`d3-contour@4.0.2`** named exports (`contours`, `contourDensity` only). Method-level surface is documented in [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md).

```python
from pyd3js_contour import contourDensity, contours

c = contours().size([10, 10]).thresholds([0.5])
polys = c([0.0] * 100)

d = contourDensity().thresholds([0.01, 0.05])
density_polys = d([[50.0, 50.0]])
```

## Compatibility matrix

Upstream export inventory (`docs/UPSTREAM_API.md`):

- `contours` — [oracle]
- `contourDensity` — [oracle]

## Development

From the repo root:

```bash
uv sync --group dev
uv run pytest packages/pyd3js-contour/package_tests --cov=pyd3js_contour --cov-report=term-missing
```

Optional upstream JS gate (vendored `d3-contour` + `npm install` under `packages/pyd3js-contour/upstream/d3-contour`):

```bash
uv run pytest packages/pyd3js-contour/package_tests -m upstream
```

The npm package name on the registry is `d3-contour`; this package mirrors that API in Python.
