# Upstream d3-color API inventory

Pinned upstream version: `d3-color@3.1.0` (see `upstream_lock.json`).

## Regenerate

From repo root:

```bash
node tools/oracle/list_d3_color_exports.mjs > /tmp/d3_color_exports.json
python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path("/tmp/d3_color_exports.json").read_text("utf-8"))
exports = [e["name"] for e in data["exports"]]
print("\n".join(exports))
PY
```

## Exports

- `color`
- `cubehelix`
- `gray`
- `hcl`
- `hsl`
- `lab`
- `lch`
- `rgb`
