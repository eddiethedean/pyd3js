# pyd3js-timer

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-timer.svg)](https://pypi.org/project/pyd3js-timer/)
[![Python versions](https://badgen.net/pypi/python/pyd3js-timer)](https://pypi.org/project/pyd3js-timer/)
[![License: ISC](https://badgen.net/badge/license/ISC/blue)](https://pypi.org/project/pyd3js-timer/)
[![CI](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/ci.yml)
[![Security](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml/badge.svg)](https://github.com/eddiethedean/pyd3js/actions/workflows/security.yml)

Python port of [`d3-timer`](https://github.com/d3/d3-timer).

Tracked version: see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

## What is d3-timer?

`d3-timer` is D3’s low-level timer queue: a monotonic `now()`, repeating `timer` work, one-shot `timeout`, repeating `interval`, and a synchronous `timerFlush()` to run all due callbacks. It is used by `d3-transition` and other modules for efficient, coalesced scheduling (frames vs long sleeps).

## What you get

- **Upstream export parity** for the pinned `d3-timer@3.0.1` (see [API inventory](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/UPSTREAM_API.md)).
- **100% line coverage** for `pyd3js_timer` (enforced with `--cov-fail-under=100` in this package’s pytest config and in CI).
- **Pytest ports** of the upstream Mocha suite under `package_tests/test_upstream_*.py` (a few Node-only cases are skipped with reasons: `setTimeout` counting, `this` binding).

## Install

From PyPI:

```bash
pip install pyd3js-timer
```

This repo is a uv workspace monorepo. For local development:

```bash
uv sync --group dev
```

## Dependencies

The published package has **no third-party Python dependencies** (Python standard library only, including `threading`).

## Usage

```python
from pyd3js_timer import now, timer, timer_flush, timeout, interval, Timer

t = timer(lambda elapsed: None)
t.stop()

timeout(lambda elapsed: print("once"), 100)

i = interval(lambda elapsed: print("tick"), 50)
i.stop()

timer_flush()  # run any due callbacks synchronously
```

## Stability & host differences

- **Threading**: the port uses `threading.Timer` instead of `requestAnimationFrame` / `setTimeout`. Real-time jitter and the exact “frame” schedule differ from a browser; semantics follow d3-timer’s logic (frame vs long wake, `timerFlush`, poke/skew).
- **Skipped upstream tests**: tests that monkey-patch global `setTimeout` or assert `this === undefined` are not portable; see `package_tests/test_upstream_timer.py` and `pytest` skip reasons.

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-timer/package_tests
```

Or from `packages/pyd3js-timer` (uses this package’s `pyproject` coverage gate):

```bash
cd packages/pyd3js-timer && uv run pytest
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-timer/package_tests -q --cov=pyd3js_timer --cov-report=term-missing --cov-fail-under=100
```

## Before publishing (maintainers)

Verify release readiness from the repo root:

```bash
uv run ruff check packages/pyd3js-timer
uv run ty check packages/pyd3js-timer/src
uv run pytest packages/pyd3js-timer/package_tests -q --cov=pyd3js_timer --cov-fail-under=100
uv build packages/pyd3js-timer
uv run twine check dist/pyd3js_timer-*.whl dist/pyd3js_timer-*.tar.gz
```

Confirm `version` in `packages/pyd3js-timer/pyproject.toml` matches `pyd3js_timer.__version__` and the heading for **0.1.0** in [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/CHANGELOG.md).

## Documentation

- User guide: [`docs/USER_GUIDE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/USER_GUIDE.md)
- Changelog: [`docs/CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/CHANGELOG.md)
- Upstream API inventory: [`docs/UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/UPSTREAM_API.md)
- Updating upstream: [`docs/UPSTREAM_UPDATE.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/UPSTREAM_UPDATE.md)
- Design notes: [`docs/ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-timer/docs/ROADMAP.md)
