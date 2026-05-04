# pyd3js-ease user guide

Runnable examples with **real outputs**; the test suite checks every `python` / `text` pair in this file and in `README.md`.

## Quickstart

```python
import pyd3js_ease as d3

print(d3.easeLinear(0.5))
print(d3.easeCubicIn(0.5))
print(d3.easeQuad is d3.easeQuadInOut)
print(d3.easeBounce is d3.easeBounceOut)
```

```text
0.5
0.125
True
True
```

## Polynomial easing (exponent)

Default exponent is **3** (same as upstream). Use `.exponent(e)` for a new ease:

```python
import pyd3js_ease as d3

p = d3.easePolyIn.exponent(2.5)
print(round(p(0.5), 6))
```

```text
0.176777
```

## Elastic (amplitude and period)

```python
import pyd3js_ease as d3

f = d3.easeElasticIn.amplitude(1.3).period(0.2)
print(round(f(0.5), 6))
```

```text
-0.030303
```

## Back easing (overshoot)

```python
import pyd3js_ease as d3

custom = d3.easeBackIn.overshoot(2.0)
print(round(custom(0.5), 6))
```

```text
-0.125
```

## Poly out ignores extra arguments

Like upstream `easePolyOut(t, null)`, extra positional arguments are ignored:

```python
import pyd3js_ease as d3

print(d3.easePolyOut(0.5) == d3.easePolyOut(0.5, None))
```

```text
True
```
