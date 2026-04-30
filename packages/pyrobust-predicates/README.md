# pyrobust-predicates

Python port of [mourner/robust-predicates](https://github.com/mourner/robust-predicates) (v3.0.x), providing `orient2d` / `orient2dfast` with the same **y-down** screen-coordinate convention as the JavaScript library.

This package exists to support a pure-Python [Delaunator](https://github.com/mapbox/delaunator) port (`pydelaunator`) without a Node.js subprocess.

## Install

```bash
uv add pyrobust-predicates
```

## API

- `orient2d(ax, ay, bx, by, cx, cy) -> float`
- `orient2dfast(ax, ay, bx, by, cx, cy) -> float`

## License

Unlicense (public domain), matching upstream `robust-predicates`.
