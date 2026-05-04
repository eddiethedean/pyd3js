from __future__ import annotations

from typing import Any, Callable


def interpolate_call(i: Callable[..., Any], this: Any, t: float) -> Any:
    """Invoke a tween interpolator like d3-transition's ``i.call(this, t)``."""
    try:
        return i(this, t)
    except TypeError:
        return i(t)
