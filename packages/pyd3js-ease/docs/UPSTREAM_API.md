# Upstream d3-ease API inventory

Pinned upstream version: `d3-ease@3.0.1` (see repo root [`upstream_lock.json`](https://github.com/eddiethedean/pyd3js/blob/main/upstream_lock.json)).

Python also exposes **configurator types** (`PolyIn`, `PolyOut`, `PolyInOut`, `BackIn`, `BackOut`, `BackInOut`, `ElasticIn`, `ElasticOut`, `ElasticInOut`) as explicit classes; upstream only exports the default instances from `src/index.js`.

## Exports (`src/index.js`)

- `easeLinear`
- `easeQuad`
- `easeQuadIn`
- `easeQuadOut`
- `easeQuadInOut`
- `easeCubic`
- `easeCubicIn`
- `easeCubicOut`
- `easeCubicInOut`
- `easePoly`
- `easePolyIn`
- `easePolyOut`
- `easePolyInOut`
- `easeSin`
- `easeSinIn`
- `easeSinOut`
- `easeSinInOut`
- `easeExp`
- `easeExpIn`
- `easeExpOut`
- `easeExpInOut`
- `easeCircle`
- `easeCircleIn`
- `easeCircleOut`
- `easeCircleInOut`
- `easeBounce`
- `easeBounceIn`
- `easeBounceOut`
- `easeBounceInOut`
- `easeBack`
- `easeBackIn`
- `easeBackOut`
- `easeBackInOut`
- `easeElastic`
- `easeElasticIn`
- `easeElasticOut`
- `easeElasticInOut`

## Python surface

- **Aliases** match upstream: `easeQuad` is `easeQuadInOut`, `easeBounce` is `easeBounceOut`, `easeElastic` is `easeElasticOut`, etc.
- **Configurable eases** use classes with `__call__(t)` and `.exponent`, `.overshoot`, `.amplitude`, `.period` like upstream factory functions.
- **`easePolyOut(t, *args)`** ignores extra positional arguments (parity with JS `easePolyOut(t, null)`).
