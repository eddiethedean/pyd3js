"""Helpers mirroring d3-geo `test/asserts.js` and `test/path/test-context.js`."""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path
from typing import Any

_FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_json_gz(name: str) -> Any:
    with gzip.open(_FIXTURES / name, "rt", encoding="utf-8") as f:
        return json.load(f)


def assert_in_delta(actual: Any, expected: Any, delta: float = 1e-6) -> None:
    assert _in_delta(actual, expected, delta), f"{actual!r} not within {delta} of {expected!r}"


def _in_delta(actual: Any, expected: Any, delta: float) -> bool:
    if isinstance(expected, (list, tuple)):
        if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
            return False
        return all(_in_delta(a, e, delta) for a, e in zip(actual, expected, strict=True))
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        for k in expected:
            if k not in actual or not _in_delta(actual[k], expected[k], delta):
                return False
        for k in actual:
            if k not in expected:
                return False
        return True
    return float(expected) - delta <= float(actual) <= float(expected) + delta


_re_number = re.compile(r"[-+]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[eE][-+]?\d+)?")


def _format_number(s: str) -> str:
    x = float(s)
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    return f"{x:.3f}"


def normalize_path(path: str) -> str:
    return _re_number.sub(lambda m: _format_number(m.group(0)), path)


def assert_path_equal(actual: str, expected: str) -> None:
    assert normalize_path(str(actual)) == normalize_path(str(expected))


def assert_projection_equal(
    projection: Any,
    location: list[float],
    point: list[float],
    delta: float = 1e-6,
) -> None:
    d2 = delta if delta > 1e-3 else 1e-3
    loc2 = projection(location)
    assert isinstance(loc2, (list, tuple)) and len(loc2) == 2
    assert_in_delta(loc2[0], point[0], delta)
    assert_in_delta(loc2[1], point[1], delta)
    inv = projection.invert(point)
    assert isinstance(inv, (list, tuple)) and len(inv) == 2
    assert_in_delta(inv[1], location[1], d2)
    lon_a, lon_e = float(inv[0]), float(location[0])
    dlon = abs(lon_a - lon_e) % 360
    assert dlon <= d2 or dlon >= 360 - d2


def make_test_context() -> Any:
    buffer: list[dict[str, Any]] = []

    class Ctx:
        def arc(self, x: float, y: float, r: float) -> None:
            buffer.append({"type": "arc", "x": round(x), "y": round(y), "r": r})

        def moveTo(self, x: float, y: float) -> None:
            buffer.append({"type": "moveTo", "x": round(x), "y": round(y)})

        def lineTo(self, x: float, y: float) -> None:
            buffer.append({"type": "lineTo", "x": round(x), "y": round(y)})

        def closePath(self) -> None:
            buffer.append({"type": "closePath"})

        def result(self) -> list[dict[str, Any]]:
            out = list(buffer)
            buffer.clear()
            return out

    return Ctx()
