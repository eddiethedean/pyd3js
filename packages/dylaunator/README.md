# dylaunator

Python port of [mapbox/delaunator](https://github.com/mapbox/delaunator) (v5.0.x API): fast Delaunay triangulation of 2D points using half-edge connectivity.

**Upstream pin:** logic and tests are aligned with **[mapbox/delaunator@v5.0.1](https://github.com/mapbox/delaunator/releases/tag/v5.0.1)**. See [docs/UPSTREAM_TESTS.md](docs/UPSTREAM_TESTS.md) for fixture provenance and how tests map to `test/test.js`.

Robust orientation uses **[pyrobust-predicates](https://pypi.org/project/pyrobust-predicates/)** (Python port of [mourner/robust-predicates](https://github.com/mourner/robust-predicates)), matching the JavaScript chain (`delaunator` → `robust-predicates`) used by `d3-delaunay`.

## Requirements

- **Python** 3.10+
- **Runtime dependency:** `pyrobust-predicates`

## Install

```bash
uv add dylaunator
```

## Usage

```python
from dylaunator import Delaunator

coords = [377, 479, 453, 434, 326, 387]
d = Delaunator(coords)
print(list(d.triangles))
```

Flat coordinates may be a Python `array("d", ...)` or any sequence of floats; use **`Delaunator.from_points`** for nested point lists or custom `{x, y}` objects.

## JS API mapping (mapbox/delaunator v5.0.x)

The public npm API is a **default-export class**; Python exposes the same surface with idiomatic naming where the language requires it.

| JavaScript | Python |
|------------|--------|
| `new Delaunator(coords)` | `Delaunator(coords)` |
| `Delaunator.from(points, getX?, getY?)` | `Delaunator.from_points(points, fx?, fy?, that?)` — `from` is a Python keyword, so the static factory is **`from_points`**. |
| `d.trianglesLen` | `d.triangles_len` **or** `d.trianglesLen` (same value; both supported). |
| `d.coords`, `d.triangles`, `d.halfedges`, `d.hull` | Same attribute names (`coords` is `array("d")`). |
| `d.update()` | `d.update()` |

**Also exported** (not separate npm exports, but mirror helpers inside upstream `index.js`): `flat_array`, `flat_iterable`, `default_get_x`, `default_get_y`.

Constructor validation mirrors upstream where possible (e.g. flat coords must be numeric; array-like objects with negative **`length`** raise `ValueError` with message `Invalid typed array length`).

## Testing and coverage

From the repo root (uv workspace):

```bash
uv run pytest packages/dylaunator -q
uv run pytest packages/dylaunator --cov=dylaunator --cov-report=term-missing
```

The suite includes a full port of upstream **`test/test.js`** plus small internal coverage tests. Package source is kept at **100% line coverage** under that configuration.

## Upstream test fixtures

JSON under `tests/fixtures/` matches upstream **`test/fixtures/*.json`** at v5.0.1 (byte-for-byte). Details: [docs/UPSTREAM_TESTS.md](docs/UPSTREAM_TESTS.md).

## Releasing (PyPI)

1. Publish **`pyrobust-predicates`** first (runtime dependency of this package).
2. From this directory:

```bash
uv build
uv publish  # or upload dist/* with twine
```

Built artifacts land in the workspace **`dist/`** when using uv from a package subfolder. Bump **`version`** in `pyproject.toml` and add a section to **`docs/CHANGELOG.md`** before each release.

## License

ISC (same as upstream `delaunator`).
