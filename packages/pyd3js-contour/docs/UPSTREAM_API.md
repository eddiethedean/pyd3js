# Upstream d3-contour API inventory

Pinned upstream version: `d3-contour@4.0.2` (see `upstream_lock.json`).

The published module exposes **two named exports** only (`src/index.js`). Everything else is internal to the implementation.

## Exports

- `contours`
- `contourDensity`

## `contours()` — generator interface

Aligned with the object returned by `d3.contours()` (`src/contours.js`):

| Member | Role |
| --- | --- |
| **call** `contours(values)` | Compute contour polygons for each threshold derived from `thresholds`. |
| **`.contour(values, value)`** | Single threshold isoline as a GeoJSON-like MultiPolygon dict. |
| **`.size([dx, dy])` / `.size()`** | Grid dimensions (getter returns `[dx, dy]`). |
| **`.thresholds(count \| array \| function) / .thresholds()`** | Threshold strategy or getter. |
| **`.smooth(boolean) / .smooth()`** | Linear smoothing along grid edges (getter returns bool). |

## `contourDensity()` — generator interface

Aligned with the object returned by `d3.contourDensity()` (`src/density.js`):

| Member | Role |
| --- | --- |
| **call** `density(data)` | Density contours for inferred or fixed thresholds. |
| **`.contours(data)`** | Returns a **callable** `contour(value)` with a **`.max`** getter (mirrors JS `Object.defineProperty(contour, "max", …)`). |
| **`.x`, `.y`, `.weight`** | Accessor or constant; setter returns `this`; getter returns current function. |
| **`.size`, `.cellSize`, `.thresholds`, `.bandwidth`** | Same chaining semantics as upstream; errors use `ValueError` instead of `Error`. |

Coordinate output uses plain Python lists where upstream uses GeoJSON structures; keys (`type`, `value`, `coordinates`) match GeoJSON MultiPolygon conventions.
