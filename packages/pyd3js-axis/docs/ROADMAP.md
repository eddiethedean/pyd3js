# Roadmap

- **Metapackage integration:** re-export or depend on a future full `pyd3js-selection` / `pyd3js-transition` if the monorepo adds non-stub implementations; `pyd3js-axis` will keep self-contained shims until then.
- **Optional:** run the Node oracle for SVG snapshot parity on representative scales (when `tools/oracle` is available).
- **Upstream tests:** `pytest -m upstream` runs the vendored d3-axis Mocha suite when `packages/pyd3js-axis/upstream/d3-axis` is installed.

Completed for the **3.0.0** parity target:

- `context !== selection` transition branch (synchronous end-state)
- `Selection.transition()` and `test/axis-test.js` port
