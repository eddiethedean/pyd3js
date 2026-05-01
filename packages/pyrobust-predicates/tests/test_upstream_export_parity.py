"""Parity with mourner/robust-predicates v3.0.3 `index.js` named exports."""

from __future__ import annotations

import numbers

import pyrobust_predicates as rp


def test_upstream_named_exports_present() -> None:
    expected = {
        "orient2d",
        "orient2dfast",
        "orient3d",
        "orient3dfast",
        "incircle",
        "incirclefast",
        "insphere",
        "inspherefast",
    }
    assert expected <= set(dir(rp))
    for name in expected:
        assert callable(getattr(rp, name)), name


def test_upstream_call_arity_smoke() -> None:
    """Same argument counts as JS (scalars only); returns are numeric reals."""
    assert isinstance(rp.orient2d(0, 0, 1, 1, 0, 1), numbers.Real)
    assert isinstance(rp.orient2dfast(0, 0, 1, 1, 0, 1), numbers.Real)

    assert isinstance(
        rp.orient3d(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1),
        numbers.Real,
    )
    assert isinstance(
        rp.orient3dfast(0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1),
        numbers.Real,
    )

    assert isinstance(rp.incircle(0, -1, 0, 1, 1, 0, -0.5, 0), numbers.Real)
    assert isinstance(rp.incirclefast(0, -1, 0, 1, 1, 0, -0.5, 0), numbers.Real)

    assert isinstance(
        rp.insphere(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0),
        numbers.Real,
    )
    assert isinstance(
        rp.inspherefast(1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0),
        numbers.Real,
    )
