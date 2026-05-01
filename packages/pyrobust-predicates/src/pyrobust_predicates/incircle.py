"""In-circle test (robust-predicates `esm/incircle.js` fast path + mpmath extended precision fallback)."""

from __future__ import annotations

from pyrobust_predicates._util import epsilon

iccerrboundA = (10 + 96 * epsilon) * epsilon


def _incircle_mpmath(ax: float, ay: float, bx: float, by: float, cx: float, cy: float, dx: float, dy: float) -> float:
    from mpmath import det, matrix, mp, mpf

    mp.dps = 120

    def row(x: float, y: float) -> list:
        x_, y_ = mpf(str(x)), mpf(str(y))
        return [x_, y_, x_ * x_ + y_ * y_, 1]

    M = matrix([row(ax, ay), row(bx, by), row(cx, cy), row(dx, dy)])
    return float(det(M))


def incircle(ax: float, ay: float, bx: float, by: float, cx: float, cy: float, dx: float, dy: float) -> float:
    adx = ax - dx
    bdx = bx - dx
    cdx = cx - dx
    ady = ay - dy
    bdy = by - dy
    cdy = cy - dy

    bdxcdy = bdx * cdy
    cdxbdy = cdx * bdy
    alift = adx * adx + ady * ady

    cdxady = cdx * ady
    adxcdy = adx * cdy
    blift = bdx * bdx + bdy * bdy

    adxbdy = adx * bdy
    bdxady = bdx * ady
    clift = cdx * cdx + cdy * cdy

    det = alift * (bdxcdy - cdxbdy) + blift * (cdxady - adxcdy) + clift * (adxbdy - bdxady)

    permanent = (abs(bdxcdy) + abs(cdxbdy)) * alift + (abs(cdxady) + abs(adxcdy)) * blift + (abs(adxbdy) + abs(bdxady)) * clift

    errbound = iccerrboundA * permanent

    if det > errbound or -det > errbound:
        return det
    return _incircle_mpmath(ax, ay, bx, by, cx, cy, dx, dy)


def incirclefast(ax: float, ay: float, bx: float, by: float, cx: float, cy: float, dx: float, dy: float) -> float:
    adx = ax - dx
    ady = ay - dy
    bdx = bx - dx
    bdy = by - dy
    cdx = cx - dx
    cdy = cy - dy

    abdet = adx * bdy - bdx * ady
    bcdet = bdx * cdy - cdx * bdy
    cadet = cdx * ady - adx * cdy
    alift = adx * adx + ady * ady
    blift = bdx * bdx + bdy * bdy
    clift = cdx * cdx + cdy * cdy

    return alift * bcdet + blift * cadet + clift * abdet
