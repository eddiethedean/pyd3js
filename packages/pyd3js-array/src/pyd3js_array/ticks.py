"""D3-compatible `ticks` helper."""

from __future__ import annotations

import math

from pyd3js_array.tick_step import tickStep


def _tick_round(x: float, step: float) -> float:
    if step == 0 or not math.isfinite(step) or not math.isfinite(x):
        return x
    a = abs(step)
    # D3 ticks are typically rounded to a small number of decimals derived from step.
    # The +2 is a pragmatic guard against binary floating artifacts.
    digits = max(0, -int(math.floor(math.log10(a))) + 2)
    y = round(x, digits)
    return 0.0 if y == 0.0 else y


def ticks(start: float, stop: float, count: float) -> list[float]:
    """Generate tick values for a start/stop/count.

    Matches `d3.ticks` semantics, including reversed domains.
    """

    start = float(start)
    stop = float(stop)
    count = float(count)

    if count <= 0 or math.isnan(start) or math.isnan(stop) or math.isnan(count):
        return []
    if not math.isfinite(start) or not math.isfinite(stop) or not math.isfinite(count):
        return []
    if start == stop:
        return [start]

    reverse = stop < start
    if reverse:
        start, stop = stop, start

    step = tickStep(start, stop, count)
    # `tickStep` is non-None and non-zero for finite start/stop and count > 0.
    assert step is not None

    i0 = math.ceil(start / step)
    i1 = math.floor(stop / step)
    n = int(max(0, i1 - i0 + 1))
    out = [_tick_round((i0 + i) * step, step) for i in range(n)]

    if reverse:
        out.reverse()
    return out

