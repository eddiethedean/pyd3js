# Updating the `d3-axis` pin

1. Update [`/upstream_lock.json`](../../../upstream_lock.json) for `"d3-axis"`.
2. Run `uv run python scripts/vendor_upstream.py` (vendors sources under `packages/pyd3js-axis/upstream/d3-axis` when configured).
3. Re-run `uv run pytest packages/pyd3js-axis/package_tests --cov=pyd3js_axis --cov-report=term-missing` and the optional `pytest -m upstream` gate.
4. Refresh this package’s `docs/UPSTREAM_API.md` if `src/index.js` exports change.
