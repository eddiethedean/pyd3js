# Upstream d3-dispatch API inventory

Pinned upstream version: `d3-dispatch@3.0.1` (see `upstream_lock.json`).

## Regenerate

From repo root:

```bash
node - <<'NODE'
import * as mod from "d3-dispatch";
console.log(Object.keys(mod).sort().map((k) => `- \`${k}\``).join("\n"));
NODE
```

## Exports

- `dispatch`

