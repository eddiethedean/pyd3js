from __future__ import annotations


def tpmt(x: float) -> float:
    """Two power minus ten times *x* scaled to [0,1] (d3-ease `math.js`)."""
    return (pow(2.0, -10.0 * x) - 0.0009765625) * 1.0009775171065494
