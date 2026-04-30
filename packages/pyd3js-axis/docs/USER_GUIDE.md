# pyd3js-axis user guide

## What this is

`pyd3js-axis` is a Python port of [d3-axis](https://github.com/d3/d3-axis) (pinned to **3.0.0** in `upstream_lock.json`). It renders axis ticks, domain path, and labels into a small DOM-like SVG tree used for tests and snapshots.

## Transitions (d3-axis parity)

d3’s `axis(selection)` vs `axis(selection.transition())` differ: the **transition** path animates **entering** and **exiting** tick groups. In this port, `Transition` is a **synchronous** shim: there are no timers; all attributes are applied **immediately** to the **final** (end) state, matching the outcome of a completed d3 transition for the default axis implementation.

- Use `selection.transition()` to obtain a `Transition` wrapping the same selection.
- `axis(context)` uses `context.selection()` when `context` is a `Transition`, so the pattern `axis(g.transition())` selects the `context !== selection` branch in the upstream `axis.js` port.

## Quick example

```python
from pyd3js_axis import axisLeft
from pyd3js_axis._selection import create, select_node
from pyd3js_axis._svg import outer_html

# Minimal linear-like scale
class S:
    def __call__(self, x):
        return float(x)
    def domain(self, d=None):
        return (0, 1) if d is None else self
    def range(self, r=None):
        return (0, 1) if r is None else self
    def ticks(self, n=10):
        return [0, 0.5, 1]
    def tickFormat(self):
        return None
    def copy(self):
        return S()

from pyd3js_axis._svg import Element

svg = create("svg").node()
g = Element("g")
svg.append_child(g)
sel = select_node(g)
axisLeft(S())(sel.transition())
print(outer_html(svg))  # SVG string with axis markup
```

## See also

- `README.md` — compatibility matrix and export list
- `docs/UPSTREAM_API.md` — upstream export inventory
