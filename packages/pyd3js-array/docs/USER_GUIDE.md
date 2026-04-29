# pyd3js-array user guide

This guide shows the most common usage patterns for `pyd3js-array` with **runnable examples** and their **real outputs**.

All examples in this document are automatically verified by the test suite.

## Quickstart

```python
import pyd3js_array as ar

print(ar.extent([5, 1, 2, 3, 4]))
print(ar.sum([1, 2, 3]))
print(ar.mean([1, 2, 3]))
print(ar.range(2, 5))
```

```text
(1, 5)
6.0
2.0
[2.0, 3.0, 4.0]
```

## Ticks and nice domains

```python
import pyd3js_array as ar

print(ar.ticks(0, 1, 5))
print(ar.tickIncrement(0, 1, 5))
print(ar.tickStep(0, 1, 5))
print(ar.nice(0.2, 9.6, 5))
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
import pyd3js_array as ar

b = ar.bin().domain([0, 10]).thresholds([2, 4, 6, 8])
bins = b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

print([(x.x0, x.x1, len(x)) for x in bins])
```

```text
[(0.0, 2.0, 2), (2.0, 4.0, 2), (4.0, 6.0, 2), (6.0, 8.0, 2), (8.0, 10.0, 3)]
```

## Searching with bisect / bisector

```python
import pyd3js_array as ar

print(ar.bisectLeft([1, 2, 2, 3], 2))
print(ar.bisectRight([1, 2, 2, 3], 2))

people = [{"v": 1}, {"v": 2}, {"v": 2}, {"v": 3}]
print(ar.bisector(lambda d: d["v"]).right(people, 2))
```

```text
1
3
3
```

## Grouping and set helpers

```python
import pyd3js_array as ar

data = [{"k": "a", "v": 1}, {"k": "a", "v": 2}, {"k": "b", "v": 3}]
print(ar.group(data, lambda d: d["k"]))
print(ar.rollup(data, lambda vs: ar.sum(vs, lambda d, *_: d["v"]), lambda d: d["k"]))

print(ar.union([1, 2, 2], [2, 3]))
print(ar.intersection([1, 2, 2], [2, 3], [2, 4]))
print(ar.difference([1, 2, 3], [2, 4]))
print(ar.subset([2, 3], [1, 2, 3]))
print(ar.superset([1, 2, 3], [2, 3]))
```

```text
{'a': [{'k': 'a', 'v': 1}, {'k': 'a', 'v': 2}], 'b': [{'k': 'b', 'v': 3}]}
{'a': 3.0, 'b': 3.0}
[1, 2, 3]
[2]
[1, 3]
True
True
```

## Reducers and statistics

```python
import pyd3js_array as ar

print(ar.sum([1, 2, 3]))
print(ar.median([1, 2, 3, 4]))
print(ar.quantile([1, 2, 3, 4], 0.25))
print(ar.variance([1, 2, 3]))
print(ar.deviation([1, 2, 3]))
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
import pyd3js_array as ar

print(ar.ascending(1, 2))
print(ar.descending(1, 2))

a = [1, 2, 3, 4, 5]
ar.shuffle(a, 1, 4)
print(a[0], a[-1], sorted(a[1:4]))

print(ar.sort([3, 1, 2, 2]))
print(ar.rank([10, 20, 20, 30]))
x = [5, 1, 4, 3, 2]
ar.quickselect(x, 2)
print(x)

# Seedable shuffling via shuffler(random)
seq = [0.9, 0.1, 0.5, 0.3, 0.7]
i = 0

def rng():
    global i
    r = seq[i]
    i += 1
    return r

b = [1, 2, 3, 4, 5]
ar.shuffler(rng)(b, 0, 5)
print(b)
```

```text
-1.0
1.0
1 5 [2, 3, 4]
[1, 2, 2, 3]
[0, 1, 1, 3]
[2, 1, 3, 4, 5]
[3, 4, 2, 1, 5]
```

## Sequences and scanning

```python
import pyd3js_array as ar

print(ar.cross([1, 2], ["a", "b"]))
print(ar.pairs([1, 2, 3, 4]))
print(ar.zip([1, 2], ["a", "b", "c"], [True, False]))
print(ar.transpose([[1, 2, 3], ["a", "b", "c"]]))
print(ar.scan([3, 1, 2]))
```

```text
[[1, 'a'], [1, 'b'], [2, 'a'], [2, 'b']]
[[1, 2], [2, 3], [3, 4]]
[[1, 'a', True], [2, 'b', False]]
[[1, 'a'], [2, 'b'], [3, 'c']]
1
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

