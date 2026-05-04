# Upstream d3-timer API inventory

Pinned upstream version: `d3-timer@3.0.1` (see `upstream_lock.json` at the repo root).

## Entry exports (`src/index.js`)

| Export | Python (`pyd3js_timer`) |
| --- | --- |
| `now` | `now` |
| `timer` | `timer`, class `Timer` |
| `timerFlush` | `timer_flush`, alias `timerFlush` |
| `timeout` (default) | `timeout` |
| `interval` (default) | `interval`, class `IntervalTimer` |

Additional Python-only exports: `__version__`.

## Regenerate

Compare against upstream:

```bash
curl -s https://raw.githubusercontent.com/d3/d3-timer/v3.0.1/src/index.js
```
