# pyd3js-selection

Python port of [`d3-selection`](https://github.com/d3/d3-selection).

Tracked version: see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

## What you get

- **Upstream export parity** for the pinned `d3-selection@3.0.0` (see matrix below).
- **Upstream `d3-selection` JS tests vendored and passing** via a pytest gate (`-m upstream`).

## Install

From PyPI:

```bash
pip install pyd3js-selection
```

For local development (uv workspace):

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_selection as d3

doc = d3.document  # set by your environment; tests use the jsdom fixture

sel = d3.select(doc).selectAll("div")
sel = sel.data([1, 2, 3]).join("div").text(lambda d, i, nodes: d)
```

## Compatibility matrix

Pinned upstream inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-selection/docs/UPSTREAM_API.md).

Legend:

- **`[ported]`**: implemented and covered by ported upstream tests.
- **`[missing]`**: reserved for future upstream drift.

### Upstream exports (d3-selection@3.0.0)

- `create` — [ported]
- `creator` — [ported]
- `local` — [ported]
- `matcher` — [ported]
- `namespace` — [ported]
- `namespaces` — [ported]
- `pointer` — [ported]
- `pointers` — [ported]
- `select` — [ported]
- `selectAll` — [ported]
- `selection` — [ported]
- `selector` — [ported]
- `selectorAll` — [ported]
- `style` — [ported]
- `window` — [ported]
