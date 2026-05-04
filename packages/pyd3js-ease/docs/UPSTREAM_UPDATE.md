# Updating upstream `d3-ease`

1. Bump the version in repo root `upstream_lock.json` for `"d3-ease"`.
2. Vendor the tag: `uv run python scripts/vendor_upstream.py` (if using the vendored tree).
3. Diff `packages/pyd3js-ease` against upstream `src` and adjust Python.
4. Port any new/changed tests from upstream `test/`.
5. Update `docs/UPSTREAM_API.md` export list and `README.md` compatibility matrix.
6. Run quality gates:

```bash
uv run pytest packages/pyd3js-ease/package_tests --cov=pyd3js_ease --cov-report=term-missing --cov-fail-under=100
uv run ruff format packages/pyd3js-ease
uv run ruff check packages/pyd3js-ease
uv run ty check packages/pyd3js-ease/src
```

Optional: after vendoring, `cd packages/pyd3js-ease/upstream/d3-ease && npm install --legacy-peer-deps` and run the upstream Mocha suite locally for comparison.
