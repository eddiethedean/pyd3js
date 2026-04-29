# pyd3js

Python ports of [D3](https://github.com/d3/d3) modules.

This is a **uv workspace monorepo** that contains one Python distribution per upstream `d3-*` module, plus an umbrella `pyd3js` package.

Pinned upstream versions live in [`upstream_lock.json`](./upstream_lock.json).

## Packages

All distributions live under [`packages/`](./packages/). Each package has its own `README.md` with module-specific API notes.

- **Umbrella**: `packages/pyd3js` (re-exports all `pyd3js-*` modules)
- **Module ports**: `packages/pyd3js-array`, `packages/pyd3js-scale`, …

## Layout

- `packages/pyd3js-*` — one distribution per upstream `d3-*` module.
- `packages/pyd3js` — umbrella package that depends on all `pyd3js-*` modules.

## Quickstart (repo)

Use [uv](https://docs.astral.sh/uv/):

```bash
uv sync --group dev
uv run pytest
```

## Quality bar (applies to all `packages/*`)

We expect production-grade ports:

- **Pinned upstream version**: parity claims are relative to `upstream_lock.json`.
- **Auditable parity**: maintain an upstream export inventory + compatibility matrix and enforce them with parity-gate tests.
- **Testing**: unit tests + oracle parity tests where feasible + a vendored upstream JS test-suite gate when available.
- **Coverage**: **100% line coverage by default** (use `# pragma: no cover` only for truly unreachable defensive guards).

The concrete standard is documented in [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md).

## Development

Common commands:

```bash
# Run all Python tests in the monorepo
uv run pytest

# Run just one package's tests
uv run pytest packages/pyd3js-array/tests
```

### Quality standards (applies to all packages)

See [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md) for the expected bar across `packages/*` (upstream pinning, auditable parity, upstream test vendoring, oracle parity where feasible, and 100% line coverage by default).

### Vendor upstream sources (tests)

```bash
uv run python scripts/vendor_upstream.py
```

Pins are recorded in [`upstream_lock.json`](upstream_lock.json).

### Node oracle (optional)

```bash
cd tools/oracle && npm install
```

Run oracle-marked tests:

```bash
uv run pytest -m oracle
```

### Convert upstream JS tests (skeleton)

```bash
uv run python scripts/tape_to_pytest.py packages/pyd3js-array/upstream/d3-array/test/min-test.js -o packages/pyd3js-array/tests/test_min_generated.py
```

The generator recognizes `it(...)` blocks and `assert.deepStrictEqual` / `assert.strictEqual`; hand-finish assertions or wire the oracle.

## Contributing

- **Small, reviewable changes**: implement one upstream export (or a tightly related cluster) per PR.
- **Keep docs and exports in sync**: update package docs and `__all__` plus the parity gates.
- **Ship with tests**: add focused unit tests; add oracle parity tests where possible.
