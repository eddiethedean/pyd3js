# Projections

## Factories and chaining

Factories such as `geoMercator()`, `geoOrthographic()`, `geoAlbers()`, `geoAlbersUsa()` return **projection objects**. Methods follow d3-geo’s chaining style and return the projection for fluent updates:

- **`translate([x, y])`** — pixel-space translation after scaling (defaults resemble d3’s map defaults).
- **`scale(k)`** — scales projected coordinates.
- **`center([lon, lat])`** and **`rotate([λ, φ, γ])`** — orient the sphere before projecting (degrees).
- **`clipAngle`**, **`clipExtent`**, **`preclip` / `postclip`** — control clipping pipelines (antimeridian, circle, rectangle).

Each projection is callable as `projection([lon, lat])`. Composite **`geoAlbersUsa`** multiplexes the lower 48, Alaska, and Hawaii regions with disjoint clip extents; points outside all regions may yield `None`.

## Fit helpers

For laying out content to a viewport, use the same helpers as d3-geo:

- **`fitExtent([[x0, y0], [x1, y1]], object)`**
- **`fitSize([width, height], object)`**
- **`fitWidth(width, object)`** / **`fitHeight(height, object)`**

`object` may be a GeoJSON geometry, Feature, FeatureCollection, or **Sphere** sentinel (`{"type": "Sphere"}`) depending on what you need to frame.

## Raw projection math

Symbols ending in **`Raw`** (for example `geoMercatorRaw`) expose the planar forward formulas without rotation, scale, or clipping. Advanced users compose these via **`geoProjection`** / **`geoProjectionMutator`** when porting custom JS pipelines.

## Practical notes

- **Identity projection** (`geoIdentity`) is useful for planar GeoJSON in pixel coordinates (still supports clip extents and transforms analogous to d3).
- **Mercator** variants wrap longitude like d3; polar caps remain singularities by nature.
- Numerical defaults match the pinned upstream version in [`upstream_lock.json`](https://github.com/eddiethedean/pyd3/blob/main/upstream_lock.json).

See [`USER_GUIDE.md`](../USER_GUIDE.md) for copy-paste Mercator path examples.
