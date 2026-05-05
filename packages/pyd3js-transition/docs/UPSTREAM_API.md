# Upstream API inventory — `d3-transition@3.0.1`

Pinned version: [`upstream_lock.json`](../../upstream_lock.json).

Sources: [`d3-transition` `src/index.js`](https://github.com/d3/d3-transition/blob/v3.0.1/src/index.js), [`src/transition/index.js`](https://github.com/d3/d3-transition/blob/v3.0.1/src/transition/index.js), [`src/selection/index.js`](https://github.com/d3/d3-transition/blob/v3.0.1/src/selection/index.js).

## Package entry (`src/index.js`)

| JS export | Role |
|-----------|------|
| `transition` | Factory (`selection().transition(name)` when imported default). |
| `active` | Return active `Transition` for a node + optional name, or `null`. |
| `interrupt` | Interrupt/cancel transitions by name on a node. |

Importing the package runs `./selection/index.js`, which assigns **`interrupt`** and **`transition`** on **`selection.prototype`**.

## Transition submodule (`src/transition/index.js`)

These are **not** re-exported from `src/index.js`, but they are part of the published `src` tree (advanced / deep imports):

| JS export | Role |
|-----------|------|
| `Transition` | Constructor for transition selections. |
| `newId` | Monotonic integer id for new transitions. |
| `transition` | Same factory as the package entry (default export). |

## Python mapping (`pyd3js_transition`)

| Upstream | Python |
|----------|--------|
| `transition` | `pyd3js_transition.transition` |
| `active` | `pyd3js_transition.active` |
| `interrupt` | `pyd3js_transition.interrupt` |
| `Transition` | `pyd3js_transition.Transition` |
| `newId` | `pyd3js_transition.new_id` |

Importing **`pyd3js_transition`** patches **`pyd3js_selection.selection.Selection`** with **`interrupt`** and **`transition`** (same side effect as the JS package).

Schedule storage follows JS **`node.__transition`** where applicable; this port reads **`__transition__`** first, then **`__transition`**, and writes **`__transition__`** for new schedules.
