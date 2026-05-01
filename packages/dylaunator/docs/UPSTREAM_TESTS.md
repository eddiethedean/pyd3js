# Upstream tests — dylaunator

Release history: [CHANGELOG.md](CHANGELOG.md) (package root `docs/`).

## Pin

- **Repository:** [mapbox/delaunator](https://github.com/mapbox/delaunator)
- **Tag:** [v5.0.1](https://github.com/mapbox/delaunator/releases/tag/v5.0.1)
- **Entry point:** `test/test.js` (Node `node:test`)
- **Fixtures:** `test/fixtures/*.json`

## Vendored files

This package vendors the same JSON bytes under:

`packages/dylaunator/tests/fixtures/`

Files: `ukraine.json`, `issue13.json`, `issue43.json`, `issue44.json`, `robustness1.json` … `robustness4.json`.

## Python mapping

| Upstream | Python |
|----------|--------|
| `test/test.js` | `tests/test_upstream_delaunator_js_port.py` |
| `validate`, `sum`, `orient`, `convex` in JS | `tests/upstream_validate.py` |
| Extra branch / edge coverage | `tests/test_internals_coverage.py` |
| Package smoke tests | `tests/test_delaunator.py` |

## Running tests

From monorepo root:

```bash
uv run pytest packages/dylaunator -q
```

## Coverage

```bash
uv run pytest packages/dylaunator --cov=dylaunator --cov-report=term-missing
```

Target: **100%** line coverage on `src/dylaunator/` (see package README). A small number of defensive branches are marked `# pragma: no cover` where no realistic input reproduces them.
