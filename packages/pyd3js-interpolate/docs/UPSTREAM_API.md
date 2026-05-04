# Upstream d3-interpolate API inventory

Pinned upstream version: `d3-interpolate@3.0.1` (see repo root [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json)).

Python also exposes **`isNumberArray`** / **`is_number_array`** (the JS helper lives on `interpolateNumberArray`’s module in some builds; this port exports it explicitly for typed-buffer checks).

## Exports (`src/index.js`)

- `interpolate`
- `interpolateArray`
- `interpolateBasis`
- `interpolateBasisClosed`
- `interpolateDate`
- `interpolateDiscrete`
- `interpolateHue`
- `interpolateNumber`
- `interpolateNumberArray`
- `interpolateObject`
- `interpolateRound`
- `interpolateString`
- `interpolateTransformCss`
- `interpolateTransformSvg`
- `interpolateZoom`
- `interpolateRgb`
- `interpolateRgbBasis`
- `interpolateRgbBasisClosed`
- `interpolateHsl`
- `interpolateHslLong`
- `interpolateLab`
- `interpolateHcl`
- `interpolateHclLong`
- `interpolateCubehelix`
- `interpolateCubehelixLong`
- `piecewise`
- `quantize`

## Python surface

The package mirrors **camelCase** names on the module (D3 parity) and adds **snake_case** functions (e.g. `interpolate_rgb`, `interpolate_value` for the default `interpolate` export). Color factories expose **`.gamma`** like upstream (`interpolateRgb.gamma`, `interpolateCubehelix.gamma`, etc.).
