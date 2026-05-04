# pyd3js-geo

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-geo.svg)](https://pypi.org/project/pyd3js-geo/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-geo)](https://pypi.org/project/pyd3js-geo/)
[![License](https://img.shields.io/pypi/l/pyd3js-geo.svg)](https://pypi.org/project/pyd3js-geo/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-geo`](https://github.com/d3/d3-geo).

Tracked upstream version: [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json) (`d3-geo` **3.1.1**).

## What is d3-geo?

`d3-geo` is D3’s geographic module: spherical geometry (distance, area, bounds), GeoJSON streaming, graticules, and cartographic projections. This package brings the same **public API names** and workflows to Python using plain GeoJSON-shaped `dict` / `list` objects.

## What you get

- **Upstream export parity** for the pinned `d3-geo@3.1.1` [`index.js`](https://github.com/d3/d3-geo/blob/v3.1.1/src/index.js): see the compatibility matrix below (nothing marked `[missing]`).
- **Always-on tests**: smoke tests, README / user guide examples, and export-matrix consistency checks.
- **Ported upstream JS tests** under `package_tests/test_upstream_*.py`, **opt-in** via `PYD3JS_GEO_FULL_UPSTREAM=1` (see [Testing](#testing)).

## Install

From PyPI:

```bash
pip install pyd3js-geo
```

This repo is a uv workspace monorepo. For local development:

```bash
uv sync --group dev
```

## Usage

```python
from pyd3js_geo import geoDistance, geoMercator, geoPath

print(f"{geoDistance([0, 0], [90, 0]):.12f}")

projection = geoMercator().translate([0, 0]).scale(1)
path = geoPath(projection)
line = {"type": "LineString", "coordinates": [[0, 0], [1, 0]]}
print(path(line))
```

```text
1.570796326795
M0,0L0.017,0
```

Projection factories return configurable objects (center, scale, clip, fit helpers, etc.), mirroring d3-geo’s chaining style in Python.

## Stability & intentional differences

- **Python vs JavaScript**: no browser canvas; PNG snapshot tests from upstream are not ported.
- **Numerical parity**: full behavioral parity with d3 is validated using the ported upstream pytest suite when enabled; a small number of cases remain skipped while composite projections (`geoAlbersUsa`) and related `fit*` paths are tightened (see `docs/ROADMAP.md`).
- **Typing**: the workspace applies targeted `ty` overrides for dynamic projection objects (mirroring JS patterns).

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-geo/docs/UPSTREAM_API.md) (`d3-geo@3.1.1`).

Legend:

- **`[implemented]`**: exported from `pyd3js_geo` and tracked in this matrix (default tests and/or doc examples; deeper parity via opt-in upstream suite).

### Upstream exports (d3-geo@3.1.1)

- `geoArea` — [implemented]
- `geoBounds` — [implemented]
- `geoCentroid` — [implemented]
- `geoCircle` — [implemented]
- `geoClipAntimeridian` — [implemented]
- `geoClipCircle` — [implemented]
- `geoClipExtent` — [implemented]
- `geoClipRectangle` — [implemented]
- `geoContains` — [implemented]
- `geoDistance` — [implemented]
- `geoGraticule` — [implemented]
- `geoGraticule10` — [implemented]
- `geoInterpolate` — [implemented]
- `geoLength` — [implemented]
- `geoPath` — [implemented]
- `geoAlbers` — [implemented]
- `geoAlbersUsa` — [implemented]
- `geoAzimuthalEqualArea` — [implemented]
- `geoAzimuthalEqualAreaRaw` — [implemented]
- `geoAzimuthalEquidistant` — [implemented]
- `geoAzimuthalEquidistantRaw` — [implemented]
- `geoConicConformal` — [implemented]
- `geoConicConformalRaw` — [implemented]
- `geoConicEqualArea` — [implemented]
- `geoConicEqualAreaRaw` — [implemented]
- `geoConicEquidistant` — [implemented]
- `geoConicEquidistantRaw` — [implemented]
- `geoEqualEarth` — [implemented]
- `geoEqualEarthRaw` — [implemented]
- `geoEquirectangular` — [implemented]
- `geoEquirectangularRaw` — [implemented]
- `geoGnomonic` — [implemented]
- `geoGnomonicRaw` — [implemented]
- `geoIdentity` — [implemented]
- `geoProjection` — [implemented]
- `geoProjectionMutator` — [implemented]
- `geoMercator` — [implemented]
- `geoMercatorRaw` — [implemented]
- `geoNaturalEarth1` — [implemented]
- `geoNaturalEarth1Raw` — [implemented]
- `geoOrthographic` — [implemented]
- `geoOrthographicRaw` — [implemented]
- `geoStereographic` — [implemented]
- `geoStereographicRaw` — [implemented]
- `geoTransverseMercator` — [implemented]
- `geoTransverseMercatorRaw` — [implemented]
- `geoRotation` — [implemented]
- `geoStream` — [implemented]
- `geoTransform` — [implemented]

## Testing

Run this package’s tests:

```bash
uv run pytest packages/pyd3js-geo/package_tests -q
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-geo/package_tests --cov=pyd3js_geo --cov-report=term-missing
```

### Ported d3-geo JS tests (opt-in)

Tests under `package_tests/test_upstream_*.py` are ported from [d3-geo `test/`](https://github.com/d3/d3-geo/tree/main/test) (v3.1.x). They are **skipped by default** so the monorepo stays green while numerical parity is finalized.

```bash
PYD3JS_GEO_FULL_UPSTREAM=1 uv run pytest packages/pyd3js-geo/package_tests -q

100% line coverage (excluding `pragma: no cover` tails) is enforced with:

`PYD3JS_GEO_FULL_UPSTREAM=1 uv run pytest packages/pyd3js-geo/package_tests --cov=pyd3js_geo --cov-fail-under=100 --cov-report=term-missing:skip-covered -q`
```

Fixtures (gzip) live in `package_tests/fixtures/` (`ny.json.gz`, `us_land.geojson.gz`, `world_land_50m.geojson.gz`, …). Canvas PNG snapshot tests are not ported (`test_upstream_snapshot.py` remains skipped).

### Lint / types

```bash
uv run ruff check packages/pyd3js-geo
uv run ty check .
```

### Build (release artifact)

```bash
uv build packages/pyd3js-geo
```

Wheels and sdists are written to the workspace **`dist/`** directory.

## Releasing (PyPI)

1. Publish **[pyd3js-array](https://pypi.org/project/pyd3js-array/)** **≥ 0.1.0** first (runtime dependency).
2. Align **`version`** in **`pyproject.toml`** with **`__version__`** in **`src/pyd3js_geo/__init__.py`**, and record changes in **`docs/CHANGELOG.md`** (dated section per release).
3. Confirm **`uv run pytest packages/pyd3js-geo/package_tests`**, **`ruff check`**, and **`ty check`** pass.
4. From the monorepo root:

```bash
uv build packages/pyd3js-geo
```

Upload **`dist/pyd3js_geo-*.whl`** and **`dist/pyd3js_geo-*.tar.gz`** (for example **`uv publish`** or **`twine upload`**).

## Documentation

- User guide: [`docs/USER_GUIDE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-geo/docs/USER_GUIDE.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-geo/docs/CHANGELOG.md)
- Roadmap / parity notes: [`docs/ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-geo/docs/ROADMAP.md)
