# Changelog

## 0.1.0 (2026-04-30)

- Initial Python port of **d3-axis@3.0.0** with:
  - `axisTop` / `axisRight` / `axisBottom` / `axisLeft`
  - Minimal d3-selection + **synchronous** `Transition` shim for the `context !== selection` code path (end-state only; no timers)
  - `Selection.transition()` / `Transition` API surface required by `axis.js`
- Ported upstream `test/axis-test.js` as `package_tests/test_upstream_port_axis_test.py`
