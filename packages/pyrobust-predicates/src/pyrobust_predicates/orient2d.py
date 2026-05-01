"""2D orientation (ported from robust-predicates `esm/orient2d.js`, y-down convention)."""

from __future__ import annotations

from pyrobust_predicates._util import epsilon, estimate, resulterrbound, splitter, sum

ccwerrboundA = (3 + 16 * epsilon) * epsilon
ccwerrboundB = (2 + 12 * epsilon) * epsilon
ccwerrboundC = (9 + 64 * epsilon) * epsilon * epsilon

B = [0.0] * 4
C1 = [0.0] * 8
C2 = [0.0] * 12
D = [0.0] * 16
_u = [0.0] * 4


def _orient2dadapt(
    ax: float, ay: float, bx: float, by: float, cx: float, cy: float, detsum: float
) -> float:
    acxtail: float
    acytail: float
    bcxtail: float
    bcytail: float
    bvirt: float
    c: float
    ahi: float
    alo: float
    bhi: float
    blo: float
    _i: float
    _j: float
    _0: float
    s1: float
    s0: float
    t1: float
    t0: float
    u3: float

    acx = ax - cx
    bcx = bx - cx
    acy = ay - cy
    bcy = by - cy

    s1 = acx * bcy
    c = splitter * acx
    ahi = c - (c - acx)
    alo = acx - ahi
    c = splitter * bcy
    bhi = c - (c - bcy)
    blo = bcy - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = acy * bcx
    c = splitter * acy
    ahi = c - (c - acy)
    alo = acy - ahi
    c = splitter * bcx
    bhi = c - (c - bcx)
    blo = bcx - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    B[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    B[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    B[2] = _j - (u3 - bvirt) + (_i - bvirt)
    B[3] = u3

    det = estimate(4, B)
    errbound = ccwerrboundB * detsum
    if det >= errbound or -det >= errbound:
        return det

    bvirt = ax - acx
    acxtail = ax - (acx + bvirt) + (bvirt - cx)
    bvirt = bx - bcx
    bcxtail = bx - (bcx + bvirt) + (bvirt - cx)
    bvirt = ay - acy
    acytail = ay - (acy + bvirt) + (bvirt - cy)
    bvirt = by - bcy
    bcytail = by - (bcy + bvirt) + (bvirt - cy)

    if acxtail == 0 and acytail == 0 and bcxtail == 0 and bcytail == 0:
        return det

    errbound = ccwerrboundC * detsum + resulterrbound * abs(det)
    det += (acx * bcytail + bcy * acxtail) - (acy * bcxtail + bcx * acytail)
    if det >= errbound or -det >= errbound:
        return det

    s1 = acxtail * bcy
    c = splitter * acxtail
    ahi = c - (c - acxtail)
    alo = acxtail - ahi
    c = splitter * bcy
    bhi = c - (c - bcy)
    blo = bcy - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = acytail * bcx
    c = splitter * acytail
    ahi = c - (c - acytail)
    alo = acytail - ahi
    c = splitter * bcx
    bhi = c - (c - bcx)
    blo = bcx - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    _u[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    _u[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    _u[2] = _j - (u3 - bvirt) + (_i - bvirt)
    _u[3] = u3
    C1len = sum(4, B, 4, _u, C1)

    s1 = acx * bcytail
    c = splitter * acx
    ahi = c - (c - acx)
    alo = acx - ahi
    c = splitter * bcytail
    bhi = c - (c - bcytail)
    blo = bcytail - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = acy * bcxtail
    c = splitter * acy
    ahi = c - (c - acy)
    alo = acy - ahi
    c = splitter * bcxtail
    bhi = c - (c - bcxtail)
    blo = bcxtail - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    _u[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    _u[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    _u[2] = _j - (u3 - bvirt) + (_i - bvirt)
    _u[3] = u3
    C2len = sum(C1len, C1, 4, _u, C2)

    s1 = acxtail * bcytail
    c = splitter * acxtail
    ahi = c - (c - acxtail)
    alo = acxtail - ahi
    c = splitter * bcytail
    bhi = c - (c - bcytail)
    blo = bcytail - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = acytail * bcxtail
    c = splitter * acytail
    ahi = c - (c - acytail)
    alo = acytail - ahi
    c = splitter * bcxtail
    bhi = c - (c - bcxtail)
    blo = bcxtail - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    _u[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    _u[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    _u[2] = _j - (u3 - bvirt) + (_i - bvirt)
    _u[3] = u3
    Dlen = sum(C2len, C2, 4, _u, D)

    return D[Dlen - 1]


def orient2d(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> float:
    detleft = (ay - cy) * (bx - cx)
    detright = (ax - cx) * (by - cy)
    det = detleft - detright

    detsum = abs(detleft + detright)
    if abs(det) >= ccwerrboundA * detsum:
        return det

    return -_orient2dadapt(ax, ay, bx, by, cx, cy, detsum)


def orient2dfast(
    ax: float, ay: float, bx: float, by: float, cx: float, cy: float
) -> float:
    return (ay - cy) * (bx - cx) - (ax - cx) * (by - cy)
