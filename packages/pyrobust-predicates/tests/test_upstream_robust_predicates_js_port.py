"""Port of mourner/robust-predicates v3.0.3 `test/test.js` (node:test) to pytest."""

from __future__ import annotations

from math import nextafter
from pathlib import Path

from pyrobust_predicates import (
    incircle,
    incirclefast,
    insphere,
    inspherefast,
    orient2d,
    orient2dfast,
    orient3d,
    orient3dfast,
)

_FIX = Path(__file__).resolve().parent / "fixtures"


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _orient2d_ref(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> int:
    from mpmath import mp, mpf

    mp.dps = 120
    ax, ay, bx, by, cx, cy = (mpf(str(v)) for v in (ax, ay, bx, by, cx, cy))
    r = (ay - cy) * (bx - cx) - (ax - cx) * (by - cy)
    if r > 0:
        return 1
    if r < 0:
        return -1
    return 0


def test_orient2d() -> None:
    assert orient2d(0, 0, 1, 1, 0, 1) < 0
    assert orient2d(0, 0, 0, 1, 1, 1) > 0
    assert orient2d(0, 0, 0.5, 0.5, 1, 1) == 0

    r = 0.95
    q = 18.0
    p = 16.8
    w = pow(2, -43)
    for i in range(128):
        for j in range(128):
            x = r + w * i / 128
            y = r + w * j / 128
            o = orient2d(x, y, q, q, p, p)
            o2 = _orient2d_ref(x, y, q, q, p, p)
            assert _sign(o) == o2, f"{x},{y}, {q},{q}, {p},{p}: {o} vs ref {o2}"

    for line in (_FIX / "orient2d.txt").read_text(encoding="utf-8").strip().splitlines():
        parts = line.split()
        _, ax, ay, bx, by, cx, cy, sign = parts
        a, b, c, d, e, f = map(float, (ax, ay, bx, by, cx, cy))
        si = int(sign)
        result = orient2d(a, b, c, d, e, f)
        assert _sign(result) == -si, f"{line}: {result} vs {-si}"


def test_orient2dfast() -> None:
    assert orient2dfast(0, 0, 1, 1, 0, 1) < 0
    assert orient2dfast(0, 0, 0, 1, 1, 1) > 0
    assert orient2dfast(0, 0, 0.5, 0.5, 1, 1) == 0


def test_incircle() -> None:
    assert incircle(0, -1, 0, 1, 1, 0, -0.5, 0) < 0
    assert incircle(0, -1, 1, 0, 0, 1, -1, 0) == 0
    assert incircle(0, -1, 0, 1, 1, 0, -1.5, 0) > 0

    a = nextafter(-1.0, 0.0)
    b = nextafter(-1.0, -2.0)
    assert incircle(1, 0, -1, 0, 0, 1, 0, a) < 0
    assert incircle(1, 0, -1, 0, 0, 1, 0, b) > 0

    x = 1e-64
    for _ in range(128):
        assert incircle(0, x, -x, -x, x, -x, 0, 0) > 0
        assert incircle(0, x, -x, -x, x, -x, 0, 2 * x) < 0
        assert incircle(0, x, -x, -x, x, -x, 0, x) == 0
        x *= 10

    for line in (_FIX / "incircle.txt").read_text(encoding="utf-8").strip().splitlines():
        parts = line.split()
        nums = list(map(float, parts[1:-1]))
        si = int(parts[-1])
        result = incircle(*nums)
        assert _sign(result) == si, f"{line}: {result} vs {si}"


def test_incirclefast() -> None:
    assert incirclefast(0, -1, 0, 1, 1, 0, -0.5, 0) < 0
    assert incirclefast(0, -1, 0, 1, 1, 0, -1, 0) == 0
    assert incirclefast(0, -1, 0, 1, 1, 0, -1.5, 0) > 0


def test_orient3d() -> None:
    assert orient3d(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1) > 0
    assert orient3d(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, -1) < 0
    assert orient3d(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0) == 0

    a = nextafter(0.0, 1.0)
    b = nextafter(0.0, -1.0)
    assert orient3d(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, a) > 0
    assert orient3d(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, b) < 0

    for line in (_FIX / "orient3d.txt").read_text(encoding="utf-8").strip().splitlines():
        parts = line.split()
        vals = list(map(float, parts[1:-1]))
        si = int(parts[-1])
        result = orient3d(*vals)
        assert _sign(result) == si, f"{line}: {result} vs {si}"
        assert _sign(result) == _sign(
            orient3d(vals[9], vals[10], vals[11], vals[3], vals[4], vals[5], vals[0], vals[1], vals[2], vals[6], vals[7], vals[8])
        )

    rng = __import__("random").Random(0)
    tol = 5.0e-14
    for _ in range(1000):
        ax = 0.5 + tol * rng.random()
        ay = 0.5 + tol * rng.random()
        az = 0.5 + tol * rng.random()
        b, c, d = 12.0, 24.0, 48.0
        assert orient3d(b, b, b, c, c, c, d, d, d, ax, ay, az) == 0
        assert orient3d(c, c, c, d, d, d, ax, ay, az, b, b, b) == 0


def test_orient3dfast() -> None:
    assert orient3dfast(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1) > 0
    assert orient3dfast(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, -1) < 0
    assert orient3dfast(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0) == 0


def test_insphere() -> None:
    assert insphere(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0) < 0
    assert insphere(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2) > 0
    assert insphere(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, -1) == 0

    a = nextafter(-1.0, 0.0)
    b = nextafter(-1.0, -2.0)
    assert insphere(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, a) < 0
    assert insphere(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, b) > 0

    for line in (_FIX / "insphere.txt").read_text(encoding="utf-8").strip().splitlines():
        parts = line.split()
        vals = list(map(float, parts[1:-1]))
        si = int(parts[-1])
        result = insphere(*vals)
        assert _sign(result) == -si, f"{line}: {result} vs {-si}"


def test_inspherefast() -> None:
    assert inspherefast(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0) < 0
    assert inspherefast(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2) > 0
    assert inspherefast(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, -1) == 0
