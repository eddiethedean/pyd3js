# Upstream tests — pyrobust-predicates

Release history: [CHANGELOG.md](CHANGELOG.md) (package root `docs/`).

## Pin

- **Repository:** [mourner/robust-predicates](https://github.com/mourner/robust-predicates)
- **Tag:** [v3.0.3](https://github.com/mourner/robust-predicates/releases/tag/v3.0.3)
- **Entry point:** `test/test.js` (Node `node:test`)
- **Fixtures:** `test/fixtures/*.txt` (`orient2d.txt`, `incircle.txt`, `orient3d.txt`, `insphere.txt`)

## Vendored files

This package vendors the same `.txt` bytes under:

`packages/pyrobust-predicates/tests/fixtures/`

## Python mapping

| Upstream | Python |
|----------|--------|
| `test/test.js` | `tests/test_upstream_robust_predicates_js_port.py` |
| `robust-orientation` grid (128×128) | High-precision reference in Python (`mpmath`) — same sign checks |
| `nextafter` (npm) | `math.nextafter` |
| Named exports vs `index.js` | `tests/test_upstream_export_parity.py` |
| `_util` helpers | `tests/test_util_internals.py` |
| Legacy well-conditioned checks | `tests/test_orient2d.py` |

## Running tests

From monorepo root:

```bash
uv run pytest packages/pyrobust-predicates -q
```

## Coverage

```bash
uv run pytest packages/pyrobust-predicates --cov=pyrobust_predicates --cov-report=term-missing
```

Target: **100%** line coverage on `src/pyrobust_predicates/`. One branch in `orient3dadapt` is marked `# pragma: no cover` where float64 inputs in CI do not hit the “all tails exactly zero” early return after the B-boundary check.

## Implementation note

`incircle` / `insphere` use **`mpmath`** for determinants when the float-stage error bound is exceeded; upstream uses full expansion code in `esm/`. Signs are validated against the vendored fixtures and the same `test.js` structure.
