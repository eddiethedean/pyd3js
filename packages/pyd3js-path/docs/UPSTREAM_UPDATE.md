# Upstream update checklist

Pinned upstream version lives in `upstream_lock.json`.

When bumping `d3-path`, do the following:

1. **Vendor upstream**:

```bash
uv run python scripts/vendor_upstream.py
```

2. **Update export inventory** (`docs/UPSTREAM_API.md`):
   - Confirm exports from `packages/pyd3js-path/upstream/d3-path/src/index.js`.
   - Update this package’s compatibility matrix in `README.md` to cover every export.

3. **Run Python tests + coverage**:

```bash
uv run pytest packages/pyd3js-path/package_tests --cov=pyd3js_path --cov-report=term-missing
```

4. **Run oracle parity tests** (if available):

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-path/package_tests
```

5. **Run upstream JS suite gate**:

```bash
cd packages/pyd3js-path/upstream/d3-path && npm install
uv run pytest -m upstream packages/pyd3js-path/package_tests
```

