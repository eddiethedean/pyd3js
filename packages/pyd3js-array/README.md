# pyd3js-array

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
from pyd3js_array import extent, min, max, range

extent([5, 1, 2, 3, 4])  # (1, 5)
min([5, 1, 2, 3, 4])     # 1
max([5, 1, 2, 3, 4])     # 5
range(2, 5)              # [2, 3, 4]
```

Accessors receive `(d, i, array)` (mirroring D3):

```python
from pyd3js_array import extent

data = [{"value": 3}, {"value": 1}, {"value": 2}]
extent(data, lambda d, i, a: d["value"])  # (1, 3)
```

## Implemented API (currently)

- `extent(values, valueof=None)`
- `min(values, valueof=None)`
- `max(values, valueof=None)`
- `range(stop)` / `range(start, stop)` / `range(start, stop, step)`

## Testing

Run the package tests:

```bash
uv run pytest packages/pyd3js-array/tests
```

### Oracle parity tests (Node)

Some tests compare behavior against real `d3-array` via the repo’s Node oracle:

```bash
cd tools/oracle && npm install
uv run pytest -m oracle packages/pyd3js-array/tests
```

## Roadmap

See [`ROADMAP.md`](./ROADMAP.md).

## Changelog

See [`CHANGELOG.md`](./CHANGELOG.md).
