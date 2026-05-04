# Updating upstream `d3-interpolate`

1. Bump the version in repo root `upstream_lock.json` for `"d3-interpolate"`.
2. Vendor the tag: `uv run python scripts/vendor_upstream.py`
3. Diff `packages/pyd3js-interpolate/upstream/d3-interpolate/src` against this port and adjust Python.
4. Port any new/changed tests from `upstream/d3-interpolate/test/`.
5. Run `uv run pytest packages/pyd3js-interpolate/package_tests --cov=pyd3js_interpolate --cov-report=term-missing`
6. Run `uv run pytest -m upstream packages/pyd3js-interpolate/package_tests` after `npm install` in the upstream folder.
7. Update `docs/UPSTREAM_API.md` and this file’s version references.
