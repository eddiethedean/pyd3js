# Upstream update checklist

Pinned upstream version lives in `upstream_lock.json`.

When bumping `d3-chord`, do the following:

1. **Vendor upstream**:

```bash
uv run python scripts/vendor_upstream.py
```

2. **Update export inventory** (`docs/UPSTREAM_API.md`) and the README compatibility matrix.

3. **Run Python tests + coverage**:

```bash
uv run pytest packages/pyd3js-chord/package_tests --cov=pyd3js_chord --cov-report=term-missing
```

4. **Run oracle parity tests** (if available):

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-chord/package_tests
```

5. **Run upstream JS suite gate**:

```bash
cd packages/pyd3js-chord/upstream/d3-chord && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-chord/package_tests
```

