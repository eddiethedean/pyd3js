# Getting started

## What this package is

`pyd3js-geo` is a Python port of Mike Bostock’s [`d3-geo`](https://github.com/d3/d3-geo): spherical predicates (distance, containment), GeoJSON streaming, graticules, and cartographic projections. Public names mirror upstream (`geoMercator`, `geoPath`, …) so code and tutorials written for d3-geo map cleanly.

You work with **plain GeoJSON-shaped** Python structures: `dict` with `"type"` / `"coordinates"` / `"geometry"` fields and nested lists of numbers.

## Coordinates

Longitude and latitude are expressed in **degrees**, consistent with d3-geo and GeoJSON. Projection factories internally rotate and convert as needed; you rarely touch radians unless you call low-level `*Raw` projection math directly.

## Typical imports

```python
from pyd3js_geo import (
    geoDistance,
    geoMercator,
    geoPath,
    geoBounds,
)
```

The canonical listing of exported symbols is [`UPSTREAM_API.md`](../UPSTREAM_API.md). Anything listed there is available from `pyd3js_geo` (plus `__version__`).

## First runnable examples

Step-by-step snippets with exact stdout are in [`USER_GUIDE.md`](../USER_GUIDE.md): distance and interpolate, Mercator path strings, and rotation.

For installation and a minimal REPL-style demo, see the root [`README.md`](../../README.md).

## Mental model

1. **Projections** are callables: pass `[lon, lat]` in degrees → `[x, y]` in pixel-like coordinates for your chosen scale and translate. Many projections expose `.invert()` for the reverse map where defined.

2. **`geoPath(projection)`** renders geometries to SVG path `d` strings (or drives a custom canvas-like context). Without a projection, it treats coordinates as already planar.

3. **`geoStream(geometry, stream)`** walks GeoJSON and invokes `point` / `lineStart` / … on a sink. Higher-level helpers (`geoArea`, `geoBounds`, …) build streams internally.

## Where to go next

- [Projections](02-projections.md) — configuring scales, centers, clips, and `fit*` layouts.
- [GeoJSON and paths](03-geojson-paths.md) — path strings, contexts, metrics on geometries.
