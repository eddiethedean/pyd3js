# pyd3js-array

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-array.svg)](https://pypi.org/project/pyd3js-array/)

Python port of [`d3-array`](https://github.com/d3/d3-array).

Tracked version: see [upstream_lock.json](../../upstream_lock.json).

## Install

This repo is a uv workspace. For local development:

```bash
uv sync --group dev
```

To add just this package to another project (once published), you’d install `pyd3js-array` and import `pyd3js_array`.

## Usage

```python
from pyd3js_array import (
    bin,
    bisectLeft,
    bisector,
    deviation,
    extent,
    max,
    mean,
    min,
    nice,
    range,
    sum,
    ticks,
)

print(extent([5, 1, 2, 3, 4]))
print(min([5, 1, 2, 3, 4]))
print(max([5, 1, 2, 3, 4]))
print(range(2, 5))

print(ticks(0, 1, 5))
print(nice(0.2, 9.6, 5))

b = bin().domain([0, 10]).thresholds([2, 4, 6, 8])
bins = b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print([(x.x0, x.x1, len(x)) for x in bins])

print(bisectLeft([1, 2, 2, 3], 2))

people = [{"v": 1}, {"v": 2}, {"v": 2}, {"v": 3}]
print(bisector(lambda d: d["v"]).right(people, 2))

print(sum([1, 2, 3]))
print(mean([1, 2, 3]))
print(deviation([1, 2, 3]))
```

```text
(1, 5)
1
5
[2.0, 3.0, 4.0]
[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
(0.0, 10.0)
[(0.0, 2.0, 2), (2.0, 4.0, 2), (4.0, 6.0, 2), (6.0, 8.0, 2), (8.0, 10.0, 3)]
1
3
6.0
2.0
1.0
```

Accessors receive `(d, i, array)` (mirroring D3):

```python
from pyd3js_array import extent

data = [{"value": 3}, {"value": 1}, {"value": 2}]
print(extent(data, lambda d, i, a: d["value"]))
```

```text
(1, 3)
```

## Implemented API (currently)

- `extent(values, valueof=None)`
- `min(values, valueof=None)`
- `max(values, valueof=None)`
- `range(stop)` / `range(start, stop)` / `range(start, stop, step)`
- `sum(values, valueof=None)`
- `mean(values, valueof=None)`
- `median(values, valueof=None)`
- `quantile(values, p, valueof=None)`
- `quantileSorted(values, p, valueof=None)`
- `variance(values, valueof=None)`
- `deviation(values, valueof=None)`
- `least(values, compare=None)` / `greatest(values, compare=None)`
- `leastIndex(values, compare=None)` / `greatestIndex(values, compare=None)`
- `ticks(start, stop, count)`
- `tickIncrement(start, stop, count)`
- `tickStep(start, stop, count)`
- `nice(start, stop, count)`
- `bisectLeft(array, x, lo=0, hi=len(array))`
- `bisectRight(array, x, lo=0, hi=len(array))`
- `bisectCenter(array, x, lo=0, hi=len(array))`
- `bisector(compare_or_accessor)`
- `bin()` / `histogram()` (chainable factory)
- `ascending(a, b)` / `descending(a, b)`
- `shuffle(array, start=0, stop=None)`

## Stability & intentional deviations

- **Keyword conflicts**: internally we use `range_`, but the public API exports it as `range` to match D3.
- **Oracle parity limits**: oracle tests run through JSON, so some values (e.g. `Infinity`, `-0`, `NaN`) can’t be round-tripped reliably; those edge cases are covered with Python-only unit tests.
- **Non-determinism**: `shuffle()` is tested via invariants (permutation + range) rather than exact oracle equality.

## Compatibility matrix

Source of truth for planned work is [`ROADMAP.md`](./ROADMAP.md). This matrix is a quick snapshot.

- **Implemented**
  - Phase 0: `extent`, `min`, `max`, `range`
  - Phase 1: `sum`, `mean`, `median`, `quantile`, `quantileSorted`, `variance`, `deviation`, `least`, `greatest`, `leastIndex`, `greatestIndex`
  - Phase 2: `ticks`, `tickIncrement`, `tickStep`, `nice`, `bin` / `histogram`, `bisectLeft`, `bisectRight`, `bisectCenter`, `bisector`, `ascending`, `descending`, `shuffle`
- **Planned / TBD**
  - Additional `d3-array` APIs not yet ported (see roadmap)
  - Performance tuning and 1.0 stabilization work (Phase 3)

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-array/tests
```

### Oracle parity tests (Node)

Some tests compare behavior against real `d3-array` via the repo’s Node oracle:

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-array/tests
```

Notes:

- Oracle tests must use **JSON-safe** values (avoid `Infinity`, `-0`, and `NaN`).
- You can optionally enable local oracle caching by creating `packages/pyd3js-array/.env` with:
  - `ORACLE_CACHE=1`
  (do not commit it).

## Roadmap

See [`ROADMAP.md`](./ROADMAP.md).

## Changelog

See [`CHANGELOG.md`](./CHANGELOG.md).
