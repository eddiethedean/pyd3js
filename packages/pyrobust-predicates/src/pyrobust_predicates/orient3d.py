"""3D orientation (ported from robust-predicates `esm/orient3d.js`, y-down / same coords as JS)."""

from __future__ import annotations

from pyrobust_predicates._util import epsilon, estimate, resulterrbound, scale, splitter, sum

o3derrboundA = (7 + 56 * epsilon) * epsilon
o3derrboundB = (3 + 28 * epsilon) * epsilon
o3derrboundC = (26 + 288 * epsilon) * epsilon * epsilon

bc = [0.0] * 4
ca = [0.0] * 4
ab = [0.0] * 4
at_b = [0.0] * 4
at_c = [0.0] * 4
bt_c = [0.0] * 4
bt_a = [0.0] * 4
ct_a = [0.0] * 4
ct_b = [0.0] * 4
bct = [0.0] * 8
cat = [0.0] * 8
abt = [0.0] * 8
u = [0.0] * 4
_8 = [0.0] * 8
_8b = [0.0] * 8
_16 = [0.0] * 16
_12 = [0.0] * 12


class _Fin192:
    __slots__ = ("_buf", "_i")

    def __init__(self) -> None:
        self._buf = [[0.0] * 192, [0.0] * 192]
        self._i = 0

    @property
    def fin(self) -> list[float]:
        return self._buf[self._i]

    def finadd(self, finlen: int, alen: int, a: list[float]) -> int:
        src, dst = self._buf[self._i], self._buf[1 - self._i]
        nlen = sum(finlen, src, alen, a, dst)
        self._i = 1 - self._i
        return nlen


def _tailinit(
    xtail: float,
    ytail: float,
    ax: float,
    ay: float,
    bx: float,
    by: float,
    a: list[float],
    b: list[float],
) -> int:
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
    negate: float
    if xtail == 0:
        if ytail == 0:
            a[0] = 0.0
            b[0] = 0.0
            return 1
        negate = -ytail
        s1 = negate * ax
        c = splitter * negate
        ahi = c - (c - negate)
        alo = negate - ahi
        c = splitter * ax
        bhi = c - (c - ax)
        blo = ax - bhi
        a[0] = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
        a[1] = s1
        s1 = ytail * bx
        c = splitter * ytail
        ahi = c - (c - ytail)
        alo = ytail - ahi
        c = splitter * bx
        bhi = c - (c - bx)
        blo = bx - bhi
        b[0] = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
        b[1] = s1
        return 2
    if ytail == 0:
        s1 = xtail * ay
        c = splitter * xtail
        ahi = c - (c - xtail)
        alo = xtail - ahi
        c = splitter * ay
        bhi = c - (c - ay)
        blo = ay - bhi
        a[0] = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
        a[1] = s1
        negate = -xtail
        s1 = negate * by
        c = splitter * negate
        ahi = c - (c - negate)
        alo = negate - ahi
        c = splitter * by
        bhi = c - (c - by)
        blo = by - bhi
        b[0] = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
        b[1] = s1
        return 2
    s1 = xtail * ay
    c = splitter * xtail
    ahi = c - (c - xtail)
    alo = xtail - ahi
    c = splitter * ay
    bhi = c - (c - ay)
    blo = ay - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = ytail * ax
    c = splitter * ytail
    ahi = c - (c - ytail)
    alo = ytail - ahi
    c = splitter * ax
    bhi = c - (c - ax)
    blo = ax - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    a[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    a[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    a[2] = _j - (u3 - bvirt) + (_i - bvirt)
    a[3] = u3
    s1 = ytail * bx
    c = splitter * ytail
    ahi = c - (c - ytail)
    alo = ytail - ahi
    c = splitter * bx
    bhi = c - (c - bx)
    blo = bx - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = xtail * by
    c = splitter * xtail
    ahi = c - (c - xtail)
    alo = xtail - ahi
    c = splitter * by
    bhi = c - (c - by)
    blo = by - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    b[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    b[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    b[2] = _j - (u3 - bvirt) + (_i - bvirt)
    b[3] = u3
    return 4


def _tailadd(S: _Fin192, finlen: int, a: float, b: float, k: float, z: float) -> int:
    bvirt: float
    c: float
    ahi: float
    alo: float
    bhi: float
    blo: float
    _i: float
    _j: float
    _k: float
    _0: float
    s1: float
    s0: float
    u3: float
    s1 = a * b
    c = splitter * a
    ahi = c - (c - a)
    alo = a - ahi
    c = splitter * b
    bhi = c - (c - b)
    blo = b - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    c = splitter * k
    bhi = c - (c - k)
    blo = k - bhi
    _i = s0 * k
    c = splitter * s0
    ahi = c - (c - s0)
    alo = s0 - ahi
    u[0] = alo * blo - (_i - ahi * bhi - alo * bhi - ahi * blo)
    _j = s1 * k
    c = splitter * s1
    ahi = c - (c - s1)
    alo = s1 - ahi
    _0 = alo * blo - (_j - ahi * bhi - alo * bhi - ahi * blo)
    _k = _i + _0
    bvirt = _k - _i
    u[1] = _i - (_k - bvirt) + (_0 - bvirt)
    u3 = _j + _k
    u[2] = _k - (u3 - _j)
    u[3] = u3
    finlen = S.finadd(finlen, 4, u)
    if z != 0:
        c = splitter * z
        bhi = c - (c - z)
        blo = z - bhi
        _i = s0 * z
        c = splitter * s0
        ahi = c - (c - s0)
        alo = s0 - ahi
        u[0] = alo * blo - (_i - ahi * bhi - alo * bhi - ahi * blo)
        _j = s1 * z
        c = splitter * s1
        ahi = c - (c - s1)
        alo = s1 - ahi
        _0 = alo * blo - (_j - ahi * bhi - alo * bhi - ahi * blo)
        _k = _i + _0
        bvirt = _k - _i
        u[1] = _i - (_k - bvirt) + (_0 - bvirt)
        u3 = _j + _k
        u[2] = _k - (u3 - _j)
        u[3] = u3
        finlen = S.finadd(finlen, 4, u)
    return finlen


def _orient3dadapt(
    ax: float,
    ay: float,
    az: float,
    bx: float,
    by: float,
    bz: float,
    cx: float,
    cy: float,
    cz: float,
    dx: float,
    dy: float,
    dz: float,
    permanent: float,
) -> float:
    S = _Fin192()
    bvirt: float
    c: float
    ahi: float
    alo: float
    bhi: float
    blo: float
    _i: float
    _j: float
    _k: float
    _0: float
    s1: float
    s0: float
    t1: float
    t0: float
    u3: float

    adx = ax - dx
    bdx = bx - dx
    cdx = cx - dx
    ady = ay - dy
    bdy = by - dy
    cdy = cy - dy
    adz = az - dz
    bdz = bz - dz
    cdz = cz - dz

    s1 = bdx * cdy
    c = splitter * bdx
    ahi = c - (c - bdx)
    alo = bdx - ahi
    c = splitter * cdy
    bhi = c - (c - cdy)
    blo = cdy - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = cdx * bdy
    c = splitter * cdx
    ahi = c - (c - cdx)
    alo = cdx - ahi
    c = splitter * bdy
    bhi = c - (c - bdy)
    blo = bdy - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    bc[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    bc[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    bc[2] = _j - (u3 - bvirt) + (_i - bvirt)
    bc[3] = u3
    s1 = cdx * ady
    c = splitter * cdx
    ahi = c - (c - cdx)
    alo = cdx - ahi
    c = splitter * ady
    bhi = c - (c - ady)
    blo = ady - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = adx * cdy
    c = splitter * adx
    ahi = c - (c - adx)
    alo = adx - ahi
    c = splitter * cdy
    bhi = c - (c - cdy)
    blo = cdy - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    ca[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    ca[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    ca[2] = _j - (u3 - bvirt) + (_i - bvirt)
    ca[3] = u3
    s1 = adx * bdy
    c = splitter * adx
    ahi = c - (c - adx)
    alo = adx - ahi
    c = splitter * bdy
    bhi = c - (c - bdy)
    blo = bdy - bhi
    s0 = alo * blo - (s1 - ahi * bhi - alo * bhi - ahi * blo)
    t1 = bdx * ady
    c = splitter * bdx
    ahi = c - (c - bdx)
    alo = bdx - ahi
    c = splitter * ady
    bhi = c - (c - ady)
    blo = ady - bhi
    t0 = alo * blo - (t1 - ahi * bhi - alo * bhi - ahi * blo)
    _i = s0 - t0
    bvirt = s0 - _i
    ab[0] = s0 - (_i + bvirt) + (bvirt - t0)
    _j = s1 + _i
    bvirt = _j - s1
    _0 = s1 - (_j - bvirt) + (_i - bvirt)
    _i = _0 - t1
    bvirt = _0 - _i
    ab[1] = _0 - (_i + bvirt) + (bvirt - t1)
    u3 = _j + _i
    bvirt = u3 - _j
    ab[2] = _j - (u3 - bvirt) + (_i - bvirt)
    ab[3] = u3

    lmid = sum(scale(4, bc, adz, _8), _8, scale(4, ca, bdz, _8b), _8b, _16)
    finlen = sum(lmid, _16, scale(4, ab, cdz, _8), _8, S.fin)

    det = estimate(finlen, S.fin)
    errbound = o3derrboundB * permanent
    if det >= errbound or -det >= errbound:
        return det

    bvirt = ax - adx
    adxtail = ax - (adx + bvirt) + (bvirt - dx)
    bvirt = bx - bdx
    bdxtail = bx - (bdx + bvirt) + (bvirt - dx)
    bvirt = cx - cdx
    cdxtail = cx - (cdx + bvirt) + (bvirt - dx)
    bvirt = ay - ady
    adytail = ay - (ady + bvirt) + (bvirt - dy)
    bvirt = by - bdy
    bdytail = by - (bdy + bvirt) + (bvirt - dy)
    bvirt = cy - cdy
    cdytail = cy - (cdy + bvirt) + (bvirt - dy)
    bvirt = az - adz
    adztail = az - (adz + bvirt) + (bvirt - dz)
    bvirt = bz - bdz
    bdztail = bz - (bdz + bvirt) + (bvirt - dz)
    bvirt = cz - cdz
    cdztail = cz - (cdz + bvirt) + (bvirt - dz)

    if (
        adxtail == 0
        and bdxtail == 0
        and cdxtail == 0
        and adytail == 0
        and bdytail == 0
        and cdytail == 0
        and adztail == 0
        and bdztail == 0
        and cdztail == 0
    ):
        return det

    errbound = o3derrboundC * permanent + resulterrbound * abs(det)
    det += (
        adz * (bdx * cdytail + cdy * bdxtail - (bdy * cdxtail + cdx * bdytail))
        + adztail * (bdx * cdy - bdy * cdx)
        + bdz * (cdx * adytail + ady * cdxtail - (cdy * adxtail + adx * cdytail))
        + bdztail * (cdx * ady - cdy * adx)
        + cdz * (adx * bdytail + bdy * adxtail - (ady * bdxtail + bdx * adytail))
        + cdztail * (adx * bdy - ady * bdx)
    )
    if det >= errbound or -det >= errbound:
        return det

    at_len = _tailinit(adxtail, adytail, bdx, bdy, cdx, cdy, at_b, at_c)
    bt_len = _tailinit(bdxtail, bdytail, cdx, cdy, adx, ady, bt_c, bt_a)
    ct_len = _tailinit(cdxtail, cdytail, adx, ady, bdx, bdy, ct_a, ct_b)

    bctlen = sum(bt_len, bt_c, ct_len, ct_b, bct)
    finlen = S.finadd(finlen, scale(bctlen, bct, adz, _16), _16)

    catlen = sum(ct_len, ct_a, at_len, at_c, cat)
    finlen = S.finadd(finlen, scale(catlen, cat, bdz, _16), _16)

    abtlen = sum(at_len, at_b, bt_len, bt_a, abt)
    finlen = S.finadd(finlen, scale(abtlen, abt, cdz, _16), _16)

    if adztail != 0:
        finlen = S.finadd(finlen, scale(4, bc, adztail, _12), _12)
        finlen = S.finadd(finlen, scale(bctlen, bct, adztail, _16), _16)
    if bdztail != 0:
        finlen = S.finadd(finlen, scale(4, ca, bdztail, _12), _12)
        finlen = S.finadd(finlen, scale(catlen, cat, bdztail, _16), _16)
    if cdztail != 0:
        finlen = S.finadd(finlen, scale(4, ab, cdztail, _12), _12)
        finlen = S.finadd(finlen, scale(abtlen, abt, cdztail, _16), _16)

    if adxtail != 0:
        if bdytail != 0:
            finlen = _tailadd(S, finlen, adxtail, bdytail, cdz, cdztail)
        if cdytail != 0:
            finlen = _tailadd(S, finlen, -adxtail, cdytail, bdz, bdztail)
    if bdxtail != 0:
        if cdytail != 0:
            finlen = _tailadd(S, finlen, bdxtail, cdytail, adz, adztail)
        if adytail != 0:
            finlen = _tailadd(S, finlen, -bdxtail, adytail, cdz, cdztail)
    if cdxtail != 0:
        if adytail != 0:
            finlen = _tailadd(S, finlen, cdxtail, adytail, bdz, bdztail)
        if bdytail != 0:
            finlen = _tailadd(S, finlen, -cdxtail, bdytail, adz, adztail)

    return S.fin[finlen - 1]


def orient3d(
    ax: float,
    ay: float,
    az: float,
    bx: float,
    by: float,
    bz: float,
    cx: float,
    cy: float,
    cz: float,
    dx: float,
    dy: float,
    dz: float,
) -> float:
    adx = ax - dx
    bdx = bx - dx
    cdx = cx - dx
    ady = ay - dy
    bdy = by - dy
    cdy = cy - dy
    adz = az - dz
    bdz = bz - dz
    cdz = cz - dz

    bdxcdy = bdx * cdy
    cdxbdy = cdx * bdy

    cdxady = cdx * ady
    adxcdy = adx * cdy

    adxbdy = adx * bdy
    bdxady = bdx * ady

    det = adz * (bdxcdy - cdxbdy) + bdz * (cdxady - adxcdy) + cdz * (adxbdy - bdxady)

    permanent = (abs(bdxcdy) + abs(cdxbdy)) * abs(adz) + (abs(cdxady) + abs(adxcdy)) * abs(bdz) + (abs(adxbdy) + abs(bdxady)) * abs(cdz)

    errbound = o3derrboundA * permanent
    if det > errbound or -det > errbound:
        return det

    return _orient3dadapt(ax, ay, az, bx, by, bz, cx, cy, cz, dx, dy, dz, permanent)


def orient3dfast(
    ax: float,
    ay: float,
    az: float,
    bx: float,
    by: float,
    bz: float,
    cx: float,
    cy: float,
    cz: float,
    dx: float,
    dy: float,
    dz: float,
) -> float:
    adx = ax - dx
    bdx = bx - dx
    cdx = cx - dx
    ady = ay - dy
    bdy = by - dy
    cdy = cy - dy
    adz = az - dz
    bdz = bz - dz
    cdz = cz - dz

    return adx * (bdy * cdz - bdz * cdy) + bdx * (cdy * adz - cdz * ady) + cdx * (ady * bdz - adz * bdy)
