# pyd3js

Python ports of [D3](https://github.com/d3/d3) modules, packaged as `pyd3js-*` under [`packages/`](packages/).

## Layout

- `packages/pyd3js-*` — one distribution per upstream `d3-*` module.
- `packages/pyd3js` — umbrella package that depends on all `pyd3js-*` modules.

## Development

Use [uv](https://docs.astral.sh/uv/):

```bash
uv sync --group dev
uv run pytest
```

### Vendor upstream sources (tests)

```bash
uv run python scripts/vendor_upstream.py
```

Pins are recorded in [`upstream_lock.json`](upstream_lock.json).

### Node oracle (optional)

```bash
cd tools/oracle && npm install
```

Use `ORACLE=1` with tests that call the oracle helper.

### Convert upstream JS tests (skeleton)

```bash
uv run python scripts/tape_to_pytest.py packages/pyd3js-array/upstream/d3-array/test/min-test.js -o packages/pyd3js-array/tests/test_min_generated.py
```

The generator recognizes `it(...)` blocks and `assert.deepStrictEqual` / `assert.strictEqual`; hand-finish assertions or wire the oracle.
