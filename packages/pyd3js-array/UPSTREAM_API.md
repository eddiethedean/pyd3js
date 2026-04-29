# Upstream d3-array API inventory

Pinned upstream version: `d3-array@3.2.4` (see `upstream_lock.json`).

## Regenerate

From repo root:

```bash
node tools/oracle/list_d3_array_exports.mjs > /tmp/d3_array_exports.json
python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("/tmp/d3_array_exports.json").read_text("utf-8"))
exports = [e["name"] for e in data["exports"]]
print("\n".join(exports))
PY
```

## Exports

- `Adder`
- `InternMap`
- `InternSet`
- `ascending`
- `bin`
- `bisect`
- `bisectCenter`
- `bisectLeft`
- `bisectRight`
- `bisector`
- `blur`
- `blur2`
- `blurImage`
- `count`
- `cross`
- `cumsum`
- `descending`
- `deviation`
- `difference`
- `disjoint`
- `every`
- `extent`
- `fcumsum`
- `filter`
- `flatGroup`
- `flatRollup`
- `fsum`
- `greatest`
- `greatestIndex`
- `group`
- `groupSort`
- `groups`
- `histogram`
- `index`
- `indexes`
- `intersection`
- `least`
- `leastIndex`
- `map`
- `max`
- `maxIndex`
- `mean`
- `median`
- `medianIndex`
- `merge`
- `min`
- `minIndex`
- `mode`
- `nice`
- `pairs`
- `permute`
- `quantile`
- `quantileIndex`
- `quantileSorted`
- `quickselect`
- `range`
- `rank`
- `reduce`
- `reverse`
- `rollup`
- `rollups`
- `scan`
- `shuffle`
- `shuffler`
- `some`
- `sort`
- `subset`
- `sum`
- `superset`
- `thresholdFreedmanDiaconis`
- `thresholdScott`
- `thresholdSturges`
- `tickIncrement`
- `tickStep`
- `ticks`
- `transpose`
- `union`
- `variance`
- `zip`
