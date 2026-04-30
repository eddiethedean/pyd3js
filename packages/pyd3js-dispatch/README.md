# pyd3js-dispatch

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-dispatch.svg)](https://pypi.org/project/pyd3js-dispatch/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-dispatch)](https://pypi.org/project/pyd3js-dispatch/)
[![License: ISC](https://badgen.net/badge/license/ISC/blue)](https://pypi.org/project/pyd3js-dispatch/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-dispatch`](https://github.com/d3/d3-dispatch).

Tracked version: see [`upstream_lock.json`](../../upstream_lock.json).

## What is a dispatch?

A **dispatch** is a small, namespaced event-listener registry. You create it with a fixed set of event
types (e.g. `"start"`, `"end"`), attach callbacks via `.on("type.namespace", fn)`, and later trigger
all callbacks of a type via `.call("type", that, *args)` / `.apply("type", that, args)`.

This pattern is used throughout D3 to provide internal events (drag/zoom/brush/transition, etc.)
without requiring a DOM or a heavyweight event system.

## What you get

- **Upstream export parity** (for the pinned `d3-dispatch@3.0.1`): the compatibility matrix below covers every upstream export; nothing is marked `[missing]`.
- **100% Python test coverage** for `pyd3js_dispatch` (run the coverage command below).

## Install

From PyPI:

```bash
pip install pyd3js-dispatch
```

This repo is a uv workspace monorepo. For local development:

```bash
uv sync --group dev
```

## Usage

```python
import pyd3js_dispatch as dd

d = dd.dispatch("start", "end")
log: list[tuple[str, int]] = []

d.on("start.foo", lambda this, x: log.append(("foo", x)))
d.call("start", None, 1)
print(log)

d.on("start.foo", None)
d.call("start", None, 2)
print(log)
```

```text
[('foo', 1)]
[('foo', 1)]
```

## Compatibility matrix (pinned upstream)

- `dispatch` — [unit]

## Development

Coverage:

```bash
uv run pytest packages/pyd3js-dispatch/package_tests --cov=pyd3js_dispatch --cov-report=term-missing
```
