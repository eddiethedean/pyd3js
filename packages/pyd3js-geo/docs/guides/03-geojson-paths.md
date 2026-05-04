# GeoJSON and paths

## Path strings

**`geoPath`** converts GeoJSON geometries into SVG-style path data (`d` attributes): moveTo / lineTo sequences for lines and polygons, arcs for points when a radius is set.

Typical pattern:

1. Build `projection = geoMercator().translate(...).scale(...)`.
2. Build `path = geoPath(projection)`.
3. Call `path(geometry)` where `geometry` is a GeoJSON object (`dict`).

Without a projection, **`geoPath()`** interprets coordinates as already planar `x, y`.

Metrics (`geoPath` methods such as **`.area`**, **`.measure`**, **`.bounds`**, **`.centroid`**) stream over geometry without emitting SVG strings; they follow d3’s planar-vs-spherical split as in upstream.

## Streaming

**`geoStream(object, stream)`** recursively walks GeoJSON:

- Dispatches **Point**, **MultiPoint**, **LineString**, **Polygon**, **Sphere**, nested Features / collections.
- Your stream implements **`point`**, **`lineStart`**, **`lineEnd`**, **`polygonStart`**, **`polygonEnd`**, and optionally **`sphere`**.

Transforms (`geoTransform`, radians wrappers, rotation adapters) wrap streams when projections pipeline geography through clipping and resampling.

## Canvas-style contexts

When **`geoPath`** is constructed with a **context** object exposing `moveTo`, `lineTo`, `arc`, `closePath`, you get the same command recording workflow as d3’s canvas render tests (without running a browser). The upstream PNG raster snapshot suite is not ported; deterministic checks exercise this pathway—see package tests under `test_upstream_snapshot.py`.

For runnable Mercator path output text, use [`USER_GUIDE.md`](../USER_GUIDE.md).
