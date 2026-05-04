# Changelog

## 0.1.0

- Initial release: full port of `d3-interpolate@3.0.1` exports.
- 100% line coverage for `pyd3js_interpolate`.
- Ported upstream Mocha behaviors to pytest; optional `-m upstream` gate runs the vendored Mocha suite.
- CSS/SVG transform interpolation uses a DOM-free parser (no `DOMMatrix` / SVG DOM).
