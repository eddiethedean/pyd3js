# pyd3js-interpolate user guide

This guide shows common usage with **runnable examples** and **real outputs**.

All examples in this document are automatically verified by the test suite.

## Quickstart

```python
import pyd3js_interpolate as d3

i = d3.interpolate(0, 10)
print(i(0.25), i(0.5), i(1.0))
```

```text
2.5 5.0 10.0
```

## Generic value and colors

```python
import pyd3js_interpolate as d3

print(d3.interpolate("#f00", "#00f")(0.5))
print(d3.interpolateRgb("steelblue", "brown")(0.5))
```

```text
rgb(128, 0, 128)
rgb(118, 86, 111)
```

## Arrays and number buffers

```python
import pyd3js_interpolate as d3
from array import array

print(list(d3.interpolate([0, 0], [10, 20])(0.5)))
print(list(d3.interpolateNumberArray([0, 0], array("d", [2.0, 4.0]))(0.5)))
```

```text
[5.0, 10.0]
[1.0, 2.0]
```

## Piecewise and quantize

```python
import pyd3js_interpolate as d3

f = d3.piecewise(d3.interpolate, [0, 2, 10])
print(f(0.25), f(0.75))
print(d3.quantize(d3.interpolate(0, 10), 5))
```

```text
1.0 6.0
[0.0, 2.5, 5.0, 7.5, 10.0]
```

## CSS transforms (DOM-free)

```python
import pyd3js_interpolate as d3

s = d3.interpolateTransformCss("translate(0px,0px)", "translate(10px,0px)")(0.5)
print("translate(" in s and "px" in s)
```

```text
True
```
