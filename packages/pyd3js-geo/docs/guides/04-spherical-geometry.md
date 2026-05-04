# Spherical geometry

## Measurements

- **`geoDistance(a, b)`** — great-circle distance between two `[lon, lat]` positions (degrees in, radians internally).
- **`geoLength(geojson)`** — length of lines/rings on the sphere.
- **`geoArea(geojson)`** — spherical area (polygon rings obey GeoJSON orientation conventions relative to d3’s algorithms).

## Predicates and containment

- **`geoContains(geometry, point)`** — point vs polygon/MultiPolygon semantics aligned with d3-geo.
- Internal spherical polygon containment (`polygon_contains` module) backs clipping and advanced tests; degrees-facing helpers exist where documented.

## Interpolation and circles

- **`geoInterpolate(a, b)`** returns an interpolator `(t) -> [lon, lat]` along the shortest arc.
- **`geoCircle`** builds spherical circles as GeoJSON polygons (radius in degrees).

## Bounds and structure

- **`geoBounds(geojson)`** returns `[[λ₀, φ₀], [λ₁, φ₁]]` in degrees—the longitudinal extent may wrap; compare upstream semantics when merging results.

## Graticules

**`geoGraticule()`** and **`geoGraticule10`** generate meridian/parallel lines as GeoJSON MultiLineStrings for map overlays, honoring configured step counts and extents.

For minimal runnable samples (distance, interpolate), see [`USER_GUIDE.md`](../USER_GUIDE.md).
