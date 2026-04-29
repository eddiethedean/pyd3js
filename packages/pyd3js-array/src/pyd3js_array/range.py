from __future__ import annotations

import math
from typing import List


def range_(*args: float) -> List[float]:
    if len(args) == 0:
        start, stop, step = 0.0, float("nan"), 1.0
    elif len(args) == 1:
        start, stop, step = 0.0, float(args[0]), 1.0
    elif len(args) == 2:
        start, stop, step = float(args[0]), float(args[1]), 1.0
    else:
        start, stop, step = float(args[0]), float(args[1]), float(args[2])
    if step == 0 or any(math.isnan(x) for x in (start, stop, step)):
        return []
    q = (stop - start) / step
    if math.isnan(q) or math.isinf(q):
        return []
    n = max(0, int(math.ceil(q)))
    return [start + i * step for i in range(n)]
