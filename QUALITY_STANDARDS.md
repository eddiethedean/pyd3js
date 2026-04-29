# Quality & parity standards (all `packages/*`)

This repo is a monorepo of Python ports of D3 modules. **Every package under [`packages/`](./packages/) is expected to meet the same bar** that we established for `pyd3js-array`.

If a package can’t meet one of these requirements for a principled reason (e.g. nondeterminism, JSON round-trip limitations), it must **document the exception explicitly** and add compensating tests.

## 1) Upstream pinning is the source of truth

- **Pins live in [`upstream_lock.json`](./upstream_lock.json)** and are the authoritative “what version are we porting?” record.
- Any parity claim must be made **relative to the pinned upstream version**.

## 2) “100% parity” must be auditable

For each package `packages/pyd3js-<x>` (porting upstream `d3-<x>`), keep an auditable record that answers:

- **What are all upstream exports for the pinned version?**
- **Which are implemented in Python and exported publicly?**
- **How do we prove parity (oracle, upstream tests, unit tests)?**

`pyd3js-array` uses:

- `UPSTREAM_API.md`: pinned upstream export inventory
- `README.md` compatibility matrix: status per export (`[oracle]`, `[unit-only: …]`, `[missing]`)
- A parity-gate test ensuring the matrix covers upstream exports and matches `__all__`

Other packages should adopt the same pattern (file names can vary, but the guarantees should not).

## 3) Tests: three complementary layers

### A) Python unit tests (always required)

- Fast, deterministic unit tests for behavior and edge cases.
- Prefer direct assertions over snapshot-style output.

### B) Oracle parity tests (when feasible)

- When parity is easiest to validate by comparing to upstream JS, use the Node oracle (`tools/oracle`).
- **Keep oracle inputs JSON-safe** when the oracle transports values through JSON (avoid `Infinity`, `-0`, `NaN`, and other non-round-trippable cases).
- If oracle parity is blocked, require **unit-only** tests plus a short rationale in docs.

### C) Vendored upstream JS test suite (when available)

- Vendor upstream sources/tests at the pinned version via:

```bash
uv run python scripts/vendor_upstream.py
```

- Add a pytest gate that runs the upstream suite (e.g. upstream Mocha tests) and assert it passes.
  - Mark it (and allow skipping) behind a pytest marker like `upstream`.
  - Don’t silently ignore failures: it should be a hard fail when dependencies are installed.

## 4) Coverage: 100% line coverage is the default

Each package should target **100% line coverage** for its Python implementation.

Run:

```bash
uv run pytest packages/pyd3js-<x>/tests --cov=pyd3js_<x> --cov-report=term-missing
```

Guidelines:

- Prefer covering branches with targeted tests.
- If a line is truly unreachable in practice (e.g. defensive guards that can’t be triggered in Python), use `# pragma: no cover` **sparingly** and only with a clear rationale.

## 5) Exports must match the parity docs

Public exports (typically `src/pyd3js_<x>/__init__.py` and `__all__`) must stay in sync with:

- the upstream export inventory
- the compatibility matrix

Add a small “parity gate” test to enforce this.

## 6) Update workflow when upstream changes

When updating a pin in `upstream_lock.json`, the minimum expected workflow is:

- re-vendor upstream sources/tests
- update inventory + compatibility docs
- run quality gates (lint/typecheck if present)
- run full pytest + coverage
- run oracle tests (if applicable)
- run vendored upstream JS suite gate (if applicable)

`pyd3js-array`’s concrete checklist is in [`packages/pyd3js-array/docs/UPSTREAM_UPDATE.md`](./packages/pyd3js-array/docs/UPSTREAM_UPDATE.md); other packages should provide an equivalent checklist for their module.

