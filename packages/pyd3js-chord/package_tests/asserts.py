from __future__ import annotations

from collections.abc import Mapping


def assert_in_delta(actual, expected, delta: float = 1e-6) -> None:
    if not _in_delta(actual, expected, delta):
        raise AssertionError(f"{actual!r} should be within {delta} of {expected!r}")


def _in_delta(actual, expected, delta: float) -> bool:
    if isinstance(expected, (list, tuple)):
        if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
            return False
        return all(
            _in_delta(a, e, delta) for a, e in zip(actual, expected, strict=True)
        )
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            return False
        for k, v in expected.items():
            if k not in actual or not _in_delta(actual[k], v, delta):
                return False
        # Ensure no extra keys.
        for k in actual:
            if k not in expected:
                return False
        return True
    if isinstance(expected, (int, float)):
        try:
            a = float(actual)
        except Exception:
            return False
        e = float(expected)
        return e - delta <= a <= e + delta
    return actual == expected
