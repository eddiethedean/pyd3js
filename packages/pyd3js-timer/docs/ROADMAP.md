# Roadmap / design notes

## Goals

- Stay aligned with pinned [`d3-timer`](https://github.com/d3/d3-timer) behavior for API-facing semantics (`now`, `timer`, `timer_flush`, `timeout`, `interval`).
- Keep `pyd3js_timer` at **100% line coverage** under normal CI (`pytest` + `--cov-fail-under=100`).

## Non-goals

- Matching browser vs Node vs Python timing jitter exactly (tests use ranges or synthetic clocks where needed).

## Possible improvements

- Optional injectable clock API for consumers (today, internal hooks target tests).
- Optional vendored upstream tree under `upstream/d3-timer` for side-by-side JS runs (same pattern as larger pyd3 packages).
