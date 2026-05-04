# User guide

`pyd3js-selection` is a Python port of [`d3-selection`](https://github.com/d3/d3-selection).

It provides D3-style selections with DOM-like manipulation APIs (`select`, `selectAll`, `append`,
`insert`, `remove`, `attr`, `style`, `classed`, `text`, `html`, `data`, `join`, …).

## Quick start

Create a detached element and populate it:

```python
import pyd3js_selection as d3

root = d3.create("div")
root.append("span").text("hi")

print(root.node().innerHTML)
```

```text
<span>hi</span>
```

## Working with data

```python
import pyd3js_selection as d3

root = d3.create("div")

root.selectAll("p").data([1, 2, 3]).join("p").text(lambda this, d, i, nodes: f"{i}:{d}")

print(root.node().innerHTML)
```

```text
<p>0:1</p><p>1:2</p><p>2:3</p>
```

