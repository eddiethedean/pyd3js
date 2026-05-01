# pyrobust-predicates

Python port of [mourner/robust-predicates](https://github.com/mourner/robust-predicates) (v3.0.x): adaptive-precision geometric predicates with the same **y-down** 2D convention as the JavaScript library.

**Upstream pin:** tests and fixtures target **[mourner/robust-predicates@v3.0.3](https://github.com/mourner/robust-predicates/releases/tag/v3.0.3)**. See [docs/UPSTREAM_TESTS.md](docs/UPSTREAM_TESTS.md) for how `test/test.js` maps to pytest.

This package backs **[dylaunator](https://pypi.org/project/dylaunator/)** (mapbox/delaunator in Python) so Delaunay code can run without Node.

## Requirements

- **Python** 3.10+
- **Runtime dependency:** `mpmath` (extended-precision fallback for `incircle` / `insphere` when the float filter is inconclusive; `orient2d` / `orient3d` follow the upstream expansion style in `esm/`)

## Install

```bash
uv add pyrobust-predicates
```

## API (matches upstream `index.js`)

Named exports are the same eight functions as npm:

| Symbol | Arguments | Role |
|--------|-----------|------|
| `orient2d`, `orient2dfast` | 6 scalars `(ax, ay, bx, by, cx, cy)` | 2D orientation |
| `orient3d`, `orient3dfast` | 12 scalars | 3D orientation |
| `incircle`, `incirclefast` | 8 scalars | In-circle |
| `insphere`, `inspherefast` | 15 scalars | In-sphere |

Returns are **numeric** (typically `float`; fast paths may yield `int`). Compare to zero for the geometric sign; **`orient2d` / `orient2dfast`** are not identical on ill-conditioned input (upstream treats robust vs fast as different entry points).

## Testing and coverage

```bash
uv run pytest packages/pyrobust-predicates -q
uv run pytest packages/pyrobust-predicates --cov=pyrobust_predicates --cov-report=term-missing
```

Includes a pytest port of upstream **`test/test.js`** (fixtures under `tests/fixtures/*.txt`), export parity checks, and small `_util` tests. Package source is kept at **100% line coverage** under that configuration.

## Upstream test fixtures

`.txt` files under `tests/fixtures/` match upstream **`test/fixtures/*.txt`** at v3.0.3. Details: [docs/UPSTREAM_TESTS.md](docs/UPSTREAM_TESTS.md).

## Releasing (PyPI)

From this directory:

```bash
uv build
uv publish  # or upload dist/* with twine
```

Artifacts are written to the workspace **`dist/`**. Bump **`version`** in `pyproject.toml` and record changes in **`docs/CHANGELOG.md`** before each release. Publish this package **before** **dylaunator**, which depends on it.

## License

Unlicense (public domain), matching upstream `robust-predicates`.
