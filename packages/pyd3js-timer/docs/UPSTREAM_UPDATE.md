# Updating upstream `d3-timer` and re-validating parity

`pyd3js-timer` is pinned via `upstream_lock.json` at the repo root.

## Checklist

1. **Update the pin** in `upstream_lock.json`.

2. **Refresh docs**

- Update [`docs/UPSTREAM_API.md`](./UPSTREAM_API.md) if exports change.
- Add a [`CHANGELOG.md`](./CHANGELOG.md) entry.

3. **Vendor sources** (optional; for running upstream Mocha locally)

```bash
uv run python scripts/vendor_upstream.py
```

4. **Quality gates** (from repo root)

```bash
uv run ruff check packages/pyd3js-timer
uv run ty check packages/pyd3js-timer/src
uv run pytest packages/pyd3js-timer/package_tests -q --cov=pyd3js_timer --cov-report=term-missing --cov-fail-under=100
```

5. **Upstream JS tests** (optional)

After vendoring and `npm install` under `packages/pyd3js-timer/upstream/d3-timer`, you can compare behavior manually; pytest ports live under `package_tests/test_upstream_*.py`.

## PyPI release (0.1.x)

Before tagging / uploading:

1. Align versions: `packages/pyd3js-timer/pyproject.toml` `version`, `src/pyd3js_timer/__init__.py` `__version__`, and `docs/CHANGELOG.md`.
2. Run the gates in step (4) above, plus:

```bash
uv build packages/pyd3js-timer
uv run twine check dist/pyd3js_timer-*.whl dist/pyd3js_timer-*.tar.gz
```

3. Upload only after `twine check` passes (wheel contains `pyd3js_timer` + packaged `LICENSE`).
