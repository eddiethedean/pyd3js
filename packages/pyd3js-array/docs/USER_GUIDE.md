# pyd3js-array user guide

This guide shows the most common usage patterns for `pyd3js-array` with **runnable examples** and their **real outputs**.

All examples in this document are automatically verified by the test suite.

## Quickstart

```python
from pyd3js_array import extent, mean, range, sum

print(extent([5, 1, 2, 3, 4]))
print(sum([1, 2, 3]))
print(mean([1, 2, 3]))
print(range(2, 5))
```

```text
(1, 5)
6.0
2.0
[2.0, 3.0, 4.0]
```

## Ticks and nice domains

```python
from pyd3js_array import nice, tickIncrement, tickStep, ticks

print(ticks(0, 1, 5))
print(tickIncrement(0, 1, 5))
print(tickStep(0, 1, 5))
print(nice(0.2, 9.6, 5))
```

```text
[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
-5.0
0.2
(0.0, 10.0)
```

## Binning / histogram

`bin()` returns a callable factory. Each returned bin is a Python `list` with `x0` and `x1` attributes.

```python
from pyd3js_array import bin

b = bin().domain([0, 10]).thresholds([2, 4, 6, 8])
bins = b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

print([(x.x0, x.x1, len(x)) for x in bins])
```

```text
[(0.0, 2.0, 2), (2.0, 4.0, 2), (4.0, 6.0, 2), (6.0, 8.0, 2), (8.0, 10.0, 3)]
```

## Searching with bisect / bisector

```python
from pyd3js_array import bisectLeft, bisectRight, bisector

print(bisectLeft([1, 2, 2, 3], 2))
print(bisectRight([1, 2, 2, 3], 2))

people = [{"v": 1}, {"v": 2}, {"v": 2}, {"v": 3}]
print(bisector(lambda d: d["v"]).right(people, 2))
```

```text
1
3
3
```

## Reducers and statistics

```python
from pyd3js_array import deviation, median, quantile, sum, variance

print(sum([1, 2, 3]))
print(median([1, 2, 3, 4]))
print(quantile([1, 2, 3, 4], 0.25))
print(variance([1, 2, 3]))
print(deviation([1, 2, 3]))
```

```text
6.0
2.5
1.75
1.0
1.0
```

## Ordering and shuffling

`shuffle()` is random; the example below demonstrates its invariants.

```python
from pyd3js_array import ascending, descending, shuffle

print(ascending(1, 2))
print(descending(1, 2))

a = [1, 2, 3, 4, 5]
shuffle(a, 1, 4)
print(a[0], a[-1], sorted(a[1:4]))
```

```text
-1.0
1.0
1 5 [2, 3, 4]
```

## Running oracle parity tests

From the repo root:

```bash
cd tools/oracle && npm ci
uv run pytest -m oracle packages/pyd3js-array/tests
```

Notes:

- Oracle parity tests must use **JSON-safe** values (avoid `Infinity`, `-0`, and `NaN`).
- Optional local caching: create `packages/pyd3js-array/.env` with `ORACLE_CACHE=1` (do not commit it).

