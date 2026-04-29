# Updating upstream `d3-array` and re-validating parity

`pyd3js-array` is pinned to a specific upstream `d3-array` version via `upstream_lock.json` at the repo root.

When you update that pin, you must regenerate the upstream export inventory and ensure the compatibility matrix and parity gates remain correct.

## Checklist

From the repo root:

1) **Update the pin**

- Edit `upstream_lock.json` (and any Node lockfile/config changes needed for `tools/oracle`).

2) **Reinstall the Node oracle**

```bash
cd tools/oracle && npm ci
```

3) **Regenerate upstream export inventory**

```bash
node tools/oracle/list_d3_array_exports.mjs > /tmp/d3_array_exports.json
python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("/tmp/d3_array_exports.json").read_text("utf-8"))
exports = [e["name"] for e in data["exports"]]
print("\n".join(exports))
PY
```

Then update:

- `packages/pyd3js-array/docs/UPSTREAM_API.md`
- `packages/pyd3js-array/README.md` compatibility matrix entries (add/remove exports, update statuses)

4) **Run parity gates + quality gates**

```bash
uv run ruff check packages/pyd3js-array
uv run ty check packages/pyd3js-array
uv run pytest packages/pyd3js-array/tests --cov=pyd3js_array --cov-report=term-missing
uv run pytest -m oracle packages/pyd3js-array/tests
```

5) **Run vendored upstream `d3-array` test suite (Mocha)**

First, vendor upstream sources (if not already present):

```bash
uv run python scripts/vendor_upstream.py
```

Then install upstream JS deps and run the pytest gate:

```bash
cd packages/pyd3js-array/upstream/d3-array && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-array/tests
```

Notes:

- Oracle parity tests must remain **JSON-safe** (avoid `Infinity`, `-0`, `NaN`).
- `packages/pyd3js-array/tests/test_parity_matrix.py` enforces that the README matrix covers the pinned upstream exports and matches `pyd3js_array.__all__`.

