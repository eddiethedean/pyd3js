# pyd3js-geo

Python port of [`d3-geo`](https://github.com/d3/d3-geo).

**API surface** matches [`d3-geo` v3.1.x `index.js`](https://github.com/d3/d3-geo/blob/main/src/index.js): `geoPath`, `geoStream`, `geoArea`, `geoBounds`, `geoCentroid`, `geoCircle`, clip helpers, `geoContains`, `geoDistance`, `geoGraticule` / `geoGraticule10`, `geoInterpolate`, `geoLength`, `geoRotation`, `geoTransform`, `geoProjection` / `geoProjectionMutator`, and the named projections plus their `*Raw` variants.

GeoJSON objects are plain `dict` / `list` structures (JSON-like), as in JavaScript.

Tracked upstream version: [`upstream_lock.json`](../../upstream_lock.json) (`d3-geo` **3.1.1**).

## Dev

```bash
uv run pytest packages/pyd3js-geo/tests -q
uv run ruff check packages/pyd3js-geo
uv run ty check .
```

### Upstream test port

Tests under `tests/test_upstream_*.py` are ported from [d3-geo `test/`](https://github.com/d3/d3-geo/tree/main/test) (v3.1.x). They are **skipped by default** so the monorepo stays green while the Python implementation catches up to full numerical parity.

Run the full ported suite (expect failures until parity is complete):

```bash
PYD3JS_GEO_FULL_UPSTREAM=1 uv run pytest packages/pyd3js-geo/tests -q
```

Fixtures (gzip) live in `tests/fixtures/` (`ny.json.gz`, `us_land.geojson.gz`, `world_land_50m.geojson.gz`, …). Canvas PNG **snapshot** tests from upstream are not ported (`test_upstream_snapshot.py` is permanently skipped).
