# pyd3js-array

[![PyPI version](https://img.shields.io/pypi/v/pyd3js-array.svg)](https://pypi.org/project/pyd3js-array/)

Python port of [`d3-array`](https://github.com/d3/d3-array).

Tracked version: see [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json).

## Status

- **100% upstream export parity** (for the pinned `d3-array@3.2.4`): the compatibility matrix below covers every upstream export; nothing is marked `[missing]`.
- **100% Python test coverage** for `pyd3js_array` (run the coverage command below).
- **100% upstream `d3-array` JS tests vendored and passing**: the upstream Mocha suite under `packages/pyd3js-array/upstream/d3-array/test/` is run via a pytest gate (`-m upstream`).

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
- `minIndex(values, valueof=None)` / `maxIndex(values, valueof=None)`
- `medianIndex(values, valueof=None)` / `quantileIndex(values, p, valueof=None)`
- `mode(values, valueof=None)`
- `range(stop)` / `range(start, stop)` / `range(start, stop, step)`
- `sum(values, valueof=None)`
- `fsum(values, valueof=None)` / `fcumsum(values, valueof=None)`
- `mean(values, valueof=None)`
- `median(values, valueof=None)`
- `quantile(values, p, valueof=None)`
- `quantileSorted(values, p, valueof=None)`
- `count(values, valueof=None)`
- `cumsum(values, valueof=None)`
- `variance(values, valueof=None)`
- `deviation(values, valueof=None)`
- `least(values, compare=None)` / `greatest(values, compare=None)`
- `leastIndex(values, compare=None)` / `greatestIndex(values, compare=None)`
- `ticks(start, stop, count)`
- `tickIncrement(start, stop, count)`
- `tickStep(start, stop, count)`
- `nice(start, stop, count)`
- `thresholdSturges(values)` / `thresholdScott(values, min, max)` / `thresholdFreedmanDiaconis(values, min, max)`
- `blur(values, r)` / `blur2(data, rx, ry=rx)` / `blurImage(imageData, rx, ry=rx)`
- `map(values, mapper)` / `filter(values, test)` / `reduce(values, reducer, value=_missing)` / `reverse(values)` / `merge(arrays)` / `every(values, test)` / `some(values, test)`
- `bisectLeft(array, x, lo=0, hi=len(array))`
- `bisectRight(array, x, lo=0, hi=len(array))`
- `bisectCenter(array, x, lo=0, hi=len(array))`
- `bisect(array, x, lo=0, hi=len(array))`
- `bisector(compare_or_accessor)`
- `bin()` / `histogram()` (chainable factory)
- `ascending(a, b)` / `descending(a, b)`
- `shuffle(array, start=0, stop=None)`
- `InternMap(iterable=None, key=None)` / `InternSet(iterable=None, key=None)`
- `group(values, *keys)`
- `groups(values, *keys)`
- `flatGroup(values, *keys)`
- `index(values, *keys)` / `indexes(values, *keys)`
- `rollup(values, reduce, *keys)` / `rollups(values, reduce, *keys)`
- `flatRollup(values, reduce, *keys)`
- `union(*iterables)` / `intersection(*iterables)` / `difference(values, other)`
- `subset(a, b)` / `superset(a, b)` / `disjoint(a, b)`
- `sort(values, compare_or_key=None)`
- `groupSort(values, reduce, key, compare=None)`
- `rank(values, compare=None)`
- `permute(values, indices)`
- `quickselect(array, k, left=0, right=None, compare=None)`
- `cross(a, b, reduce=None)`
- `pairs(values, reduce=None)`
- `zip(*iterables)` / `transpose(matrix)`
- `scan(values, compare=None)`
- `shuffler(random)`

## Stability & intentional deviations

- **Keyword conflicts**: internally we use `range_`, but the public API exports it as `range` to match D3.
- **Oracle parity limits**: oracle tests run through JSON, so some values (e.g. `Infinity`, `-0`, `NaN`) can’t be round-tripped reliably; those edge cases are covered with Python-only unit tests.
- **Non-determinism**: `shuffle()` is tested via invariants (permutation + range) rather than exact oracle equality.

## Compatibility matrix

Source of truth for planned work is [`ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-array/ROADMAP.md).

Pinned upstream inventory: [`UPSTREAM_API.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-array/UPSTREAM_API.md) (from `d3-array@3.2.4`).

Legend:

- **`[oracle]`**: implemented and has oracle parity tests for representative JSON-safe cases.
- **`[unit-only: …]`**: implemented but oracle parity is blocked/limited (e.g. JSON round-trip, nondeterminism).
- **`[missing]`**: not yet implemented.

### Upstream exports (d3-array@3.2.4)

- `Adder` — [unit-only: non-JSON class]
- `InternMap` — [oracle]
- `InternSet` — [oracle]
- `ascending` — [oracle]
- `bin` — [oracle]
- `bisect` — [oracle]
- `bisectCenter` — [oracle]
- `bisectLeft` — [oracle]
- `bisectRight` — [oracle]
- `bisector` — [oracle]
- `blur` — [oracle]
- `blur2` — [oracle]
- `blurImage` — [oracle]
- `count` — [oracle]
- `cross` — [oracle]
- `cumsum` — [oracle]
- `descending` — [oracle]
- `deviation` — [oracle]
- `difference` — [oracle]
- `disjoint` — [oracle]
- `every` — [oracle]
- `extent` — [oracle]
- `fcumsum` — [oracle]
- `filter` — [oracle]
- `flatGroup` — [oracle]
- `flatRollup` — [oracle]
- `fsum` — [oracle]
- `greatest` — [oracle]
- `greatestIndex` — [oracle]
- `group` — [oracle]
- `groupSort` — [oracle]
- `groups` — [oracle]
- `histogram` — [oracle]
- `index` — [oracle]
- `indexes` — [oracle]
- `intersection` — [oracle]
- `least` — [oracle]
- `leastIndex` — [oracle]
- `map` — [oracle]
- `max` — [oracle]
- `maxIndex` — [oracle]
- `mean` — [oracle]
- `median` — [oracle]
- `medianIndex` — [oracle]
- `merge` — [oracle]
- `min` — [oracle]
- `minIndex` — [oracle]
- `mode` — [oracle]
- `nice` — [oracle]
- `pairs` — [oracle]
- `permute` — [oracle]
- `quantile` — [oracle]
- `quantileIndex` — [oracle]
- `quantileSorted` — [oracle]
- `quickselect` — [oracle]
- `range` — [oracle]
- `rank` — [oracle]
- `reduce` — [oracle]
- `reverse` — [oracle]
- `rollup` — [oracle]
- `rollups` — [oracle]
- `scan` — [oracle]
- `shuffle` — [unit-only: nondeterministic]
- `shuffler` — [oracle]
- `some` — [oracle]
- `sort` — [oracle]
- `subset` — [oracle]
- `sum` — [oracle]
- `superset` — [oracle]
- `thresholdFreedmanDiaconis` — [oracle]
- `thresholdScott` — [oracle]
- `thresholdSturges` — [oracle]
- `tickIncrement` — [oracle]
- `tickStep` — [oracle]
- `ticks` — [oracle]
- `transpose` — [oracle]
- `union` — [oracle]
- `variance` — [oracle]
- `zip` — [oracle]

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-array/tests
```

### Coverage (Python)

```bash
uv run pytest packages/pyd3js-array/tests --cov=pyd3js_array --cov-report=term-missing
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

### Upstream `d3-array` test suite (vendored)

We vendor the pinned upstream `d3-array` repo (including its Mocha test suite) and run it via pytest.

```bash
uv run python scripts/vendor_upstream.py
cd packages/pyd3js-array/upstream/d3-array && npm install --legacy-peer-deps
uv run pytest -m upstream packages/pyd3js-array/tests
```

## Roadmap

See [`ROADMAP.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-array/ROADMAP.md).

## Changelog

See [`CHANGELOG.md`](https://github.com/eddiethedean/pyd3js/blob/main/packages/pyd3js-array/CHANGELOG.md).
