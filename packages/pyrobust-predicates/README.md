# pyrobust-predicates

Python port of [mourner/robust-predicates](https://github.com/mourner/robust-predicates) (v3.0.x), providing `orient2d` / `orient2dfast` with the same **y-down** screen-coordinate convention as the JavaScript library.

This package exists to support a pure-Python [Delaunator](https://github.com/mapbox/delaunator) port (`dylaunator`) without a Node.js subprocess.

## Install

```bash
uv add pyrobust-predicates
```

## API

- `orient2d` / `orient2dfast` — 2D orientation (`ax, ay, bx, by, cx, cy`)
- `orient3d` / `orient3dfast` — 3D orientation (12 coordinates)
- `incircle` / `incirclefast` — in-circle test (8 coordinates)
- `insphere` / `inspherefast` — in-sphere test (15 coordinates)

All return a `float` determinant-style value; compare to zero for the geometric predicate.

## Upstream test fixtures

Pytest mirrors [mourner/robust-predicates@v3.0.3](https://github.com/mourner/robust-predicates/tree/v3.0.3/test) `test/test.js` with `.txt` fixtures vendored under `tests/fixtures/` (same bytes as upstream `test/fixtures/*.txt`).

## License

Unlicense (public domain), matching upstream `robust-predicates`.
