# Upstream d3-ease API inventory

Pinned upstream version: `d3-ease@3.0.1` (see repo root [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json)).

## Exports (`src/index.js`)

- `easeLinear`
- `easeQuad` (alias of `easeQuadInOut`)
- `easeQuadIn`
- `easeQuadOut`
- `easeQuadInOut`
- `easeCubic` (alias of `easeCubicInOut`)
- `easeCubicIn`
- `easeCubicOut`
- `easeCubicInOut`
- `easePoly` (alias of `easePolyInOut`)
- `easePolyIn` (with `.exponent`)
- `easePolyOut` (with `.exponent`)
- `easePolyInOut` (with `.exponent`)
- `easeSin` (alias of `easeSinInOut`)
- `easeSinIn`
- `easeSinOut`
- `easeSinInOut`
- `easeExp` (alias of `easeExpInOut`)
- `easeExpIn`
- `easeExpOut`
- `easeExpInOut`
- `easeCircle` (alias of `easeCircleInOut`)
- `easeCircleIn`
- `easeCircleOut`
- `easeCircleInOut`
- `easeBounce` (alias of `easeBounceOut`)
- `easeBounceIn`
- `easeBounceOut`
- `easeBounceInOut`
- `easeBack` (alias of `easeBackInOut`)
- `easeBackIn` (with `.overshoot`)
- `easeBackOut` (with `.overshoot`)
- `easeBackInOut` (with `.overshoot`)
- `easeElastic` (alias of `easeElasticOut`)
- `easeElasticIn` (with `.amplitude` / `.period`)
- `easeElasticOut` (with `.amplitude` / `.period`)
- `easeElasticInOut` (with `.amplitude` / `.period`)

## Python surface

Configurable eases are **classes** with `__call__(t)` and the same **`.exponent`**, **`.overshoot`**, **`.amplitude`**, **`.period`** methods as upstream factory functions.
