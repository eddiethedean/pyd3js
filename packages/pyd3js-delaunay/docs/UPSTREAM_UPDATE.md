# Updating upstream `d3-delaunay` and re-validating parity

`pyd3js-delaunay` is pinned to **d3-delaunay@6.0.4** via [`upstream_lock.json`](../../upstream_lock.json) at the monorepo root.

This package is **pure Python**: upstream Mocha tests from `d3-delaunay` are **ported to pytest** under `package_tests/` (no vendored `npm test` gate).

## Checklist

From the repo root:

### 1) Update the pin

- Edit [`upstream_lock.json`](../../upstream_lock.json) to the new upstream tag when you intentionally move the pin.

### 2) Refresh the Python port inventory

Update as needed:

- [`docs/UPSTREAM_API.md`](UPSTREAM_API.md) — upstream exports, file mapping, ported test table.
- [`README.md`](../README.md) compatibility matrix (must stay in sync with upstream exports listed in `UPSTREAM_API.md`; `package_tests/test_parity_matrix.py` enforces this).

### 3) Port or adjust upstream tests

Upstream layout (reference): [`d3/d3-delaunay` `test/`](https://github.com/d3/d3-delaunay/tree/v6.0.4/test).

- Add or edit pytest modules under `package_tests/test_upstream_d3_delaunay_js_port_*.py` to mirror new/changed upstream cases.

### 4) Run quality gates

```bash
uv run ruff format packages/pyd3js-delaunay
uv run ruff check packages/pyd3js-delaunay
uv run ty check packages/pyd3js-delaunay
uv run pytest packages/pyd3js-delaunay/package_tests -q
```

### 5) Coverage (optional but recommended before release)

```bash
uv run pytest packages/pyd3js-delaunay/package_tests --cov=pyd3js_delaunay --cov-report=term-missing
```

### 6) Doc examples

README and user guide snippets are checked by `package_tests/test_delaunay_docs_examples.py`. After editing docs, run:

```bash
uv run pytest packages/pyd3js-delaunay/package_tests/test_delaunay_docs_examples.py -q
```
