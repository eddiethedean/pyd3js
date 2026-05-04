# Changelog

## 0.1.0

- Initial release: full port of `d3-interpolate@3.0.1` exports.
- 100% line coverage for `pyd3js_interpolate`.
- Ported upstream Mocha behaviors to pytest; optional `-m upstream` gate runs the vendored Mocha suite.
- CSS/SVG transform interpolation uses a DOM-free parser (no `DOMMatrix` / SVG DOM).
- Documentation and QA aligned with `pyd3js-array`: `docs/USER_GUIDE.md` with verified examples, README compatibility matrix, `test_interpolate_docs_examples` / `test_interpolate_parity_matrix`, package `.gitignore`, CI/security badges, and a normalized `docs/UPSTREAM_API.md` export list.
