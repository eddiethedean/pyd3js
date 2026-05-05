# pyd3js-transition

Python port of [`d3-transition`](https://github.com/d3/d3-transition).

Tracked version: see [upstream_lock.json](../../upstream_lock.json).

## Status

**Interface parity** with `d3-transition@3.0.1`: package entry exports plus the transition submodule surface (`Transition`, `newId` → `new_id`). Importing `pyd3js_transition` patches `pyd3js_selection.Selection` with `.transition` / `.interrupt`, matching the upstream side-effect import.

Inventory and mapping: [`docs/UPSTREAM_API.md`](docs/UPSTREAM_API.md).

## Compatibility matrix (`pyd3js_transition.__all__`)

| Upstream (`d3-transition`) | Python |
|----------------------------|--------|
| `transition` | `transition` |
| `active` | `active` |
| `interrupt` | `interrupt` |
| `Transition` (submodule) | `Transition` |
| `newId` (submodule) | `new_id` |

Selection prototype **`.transition`**, **`.interrupt`** — applied when this package is imported (mirrors `selection/index.js`).
