# Development and parity

## Default CI tests

From the monorepo root:

```bash
uv run pytest packages/pyd3js-geo/package_tests -q
```

This exercises smoke tests, README / user-guide doc examples, parity-matrix consistency (`docs/UPSTREAM_API.md` vs README vs `pyd3js_geo.__all__`), and other fast checks.

## Full upstream suite (opt-in)

Ported JavaScript tests live under `package_tests/test_upstream_*.py`. They are **skipped unless**:

```bash
PYD3JS_GEO_FULL_UPSTREAM=1 uv run pytest packages/pyd3js-geo/package_tests -q
```

This is the same switch you use for a **100% line coverage** gate (no `pragma: no cover` shortfall for covered lines in standard runs):

```bash
PYD3JS_GEO_FULL_UPSTREAM=1 uv run pytest packages/pyd3js-geo/package_tests \
  --cov=pyd3js_geo --cov-fail-under=100 --cov-report=term-missing:skip-covered -q
```

## Fixtures

Compressed GeoJSON fixtures live in `package_tests/fixtures/` (`*.geojson.gz`). Tests load them with helpers from `test_support.py`.

## Lint and types

```bash
uv run ruff check packages/pyd3js-geo
uv run ty check .
```

## Porting notes

- API names track **`d3-geo@3.1.1`** (`docs/UPSTREAM_API.md`).
- Browser-only PNG snapshot tests are not replicated; path-context tests substitute deterministic canvas-style command lists.
- Internal helpers retain JS-oriented structure where it keeps diffs reviewable against upstream.

For release steps, see the root package [`README.md`](../../README.md).
