# pyd3js-axis

Python port of [`d3-axis`](https://github.com/d3/d3-axis) targeting **d3-axis@3.0.0** (see [`upstream_lock.json`](../../upstream_lock.json)).

## Compatibility (d3-axis@3.0.0)

- `axisTop` — [unit + transition path + upstream test port]
- `axisRight` — [unit + transition path + upstream test port]
- `axisBottom` — [unit + transition path + upstream test port]
- `axisLeft` — [unit + transition path + upstream test port]

**Transition note:** `Selection.transition()` returns a synchronous **end-state** `Transition` (no timers). This matches the final DOM after a d3 transition for the built-in axis behavior.

## Documentation

| Doc | Purpose |
| --- | --- |
| [docs/UPSTREAM_API.md](docs/UPSTREAM_API.md) | Upstream export list |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Usage and transition semantics |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Release notes |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Follow-on work |
| [docs/UPSTREAM_UPDATE.md](docs/UPSTREAM_UPDATE.md) | How to bump the upstream pin |

## Development

```bash
uv run pytest packages/pyd3js-axis/package_tests --cov=pyd3js_axis --cov-report=term-missing
uv run ruff check packages/pyd3js-axis
uv run ty check packages/pyd3js-axis/src
```

Optional gates (when vendored / tools are present):

```bash
uv run pytest packages/pyd3js-axis/package_tests -m upstream
```
