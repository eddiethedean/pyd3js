"""JavaScript-ish coercion and comparisons used by `pyd3js-array`.

These helpers are intentionally *not* “Pythonic”; they exist to approximate D3 / JavaScript
behavior for reducers like `min`, `max`, and `extent` when inputs may be mixed types.
"""

from __future__ import annotations

import math
from typing import Any, Callable, SupportsFloat, SupportsIndex, Union


def _is_nan(x: Any) -> bool:
    return isinstance(x, float) and math.isnan(x)


def tonumber(x: Any) -> float:
    """Coerce a value to a JS-style number.

    - `None` -> `NaN`
    - `bool` -> `1.0` / `0.0`
    - `int/float` -> float
    - `str` -> float if parseable else `NaN` (empty/whitespace -> `NaN`)
    - objects with `valueOf()` -> recurse on the result

    Returns:
        A `float`, possibly `NaN`.
    """
    if x is None:
        return float("nan")
    if isinstance(x, bool):
        return 1.0 if x else 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        if s == "":
            return float("nan")
        try:
            return float(s)
        except ValueError:
            return float("nan")
    value_of = getattr(x, "valueOf", None)
    if callable(value_of):
        return tonumber(value_of())
    return float("nan")


NumberLike = Union[SupportsFloat, SupportsIndex, str, Any]


def definite(x: Any) -> bool:
    """Return True if *x* should be treated as an observed value.

    Matches the `d3-array` pattern of ignoring null/undefined and NaN-like values.

    - `None` is not definite.
    - `float('nan')` is not definite.
    - Objects with `valueOf()` are definite only if their `valueOf()` result is definite.
    - Values that raise during equality are treated as non-definite.
    """
    if x is None:
        return False
    if _is_nan(x):
        return False
    value_of = getattr(x, "valueOf", None)
    if callable(value_of):
        try:
            v = value_of()
        except Exception:
            return False
        return definite(v)
    try:
        return x == x  # noqa: PLR0124
    except Exception:
        return False


def gt(a: NumberLike, b: NumberLike) -> bool:
    """Return True if `a > b` using D3-like rules.

    - If both are strings, compare lexicographically.
    - Otherwise, coerce both to numbers and compare; any `NaN` yields False.
    """
    if isinstance(a, str) and isinstance(b, str):
        return a > b
    na, nb = tonumber(a), tonumber(b)
    if _is_nan(na) or _is_nan(nb):
        return False
    return na > nb


def lt(a: NumberLike, b: NumberLike) -> bool:
    """Return True if `a < b` using D3-like rules.

    See `gt` for the high-level rules.
    """
    if isinstance(a, str) and isinstance(b, str):
        return a < b
    na, nb = tonumber(a), tonumber(b)
    if _is_nan(na) or _is_nan(nb):
        return False
    return na < nb


Accessor = Callable[[Any, int, list[Any]], Any]
