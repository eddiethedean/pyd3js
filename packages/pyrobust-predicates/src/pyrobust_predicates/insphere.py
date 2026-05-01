"""In-sphere test (robust-predicates `esm/insphere.js` fast path + mpmath extended precision fallback)."""

from __future__ import annotations

from pyrobust_predicates._util import epsilon

isperrboundA = (16 + 224 * epsilon) * epsilon


def _insphere_mpmath(
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
    ex: float,
    ey: float,
    ez: float,
) -> float:
    from mpmath import det, matrix, mp, mpf

    mp.dps = 120

    def row(x: float, y: float, z: float) -> list:
        x_, y_, z_ = mpf(str(x)), mpf(str(y)), mpf(str(z))
        return [x_, y_, z_, x_ * x_ + y_ * y_ + z_ * z_, 1]

    M = matrix(
        [
            row(ax, ay, az),
            row(bx, by, bz),
            row(cx, cy, cz),
            row(dx, dy, dz),
            row(ex, ey, ez),
        ]
    )
    return float(det(M))


def insphere(
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
    ex: float,
    ey: float,
    ez: float,
) -> float:
    aex = ax - ex
    bex = bx - ex
    cex = cx - ex
    dex = dx - ex
    aey = ay - ey
    bey = by - ey
    cey = cy - ey
    dey = dy - ey
    aez = az - ez
    bez = bz - ez
    cez = cz - ez
    dez = dz - ez

    aexbey = aex * bey
    bexaey = bex * aey
    ab = aexbey - bexaey
    bexcey = bex * cey
    cexbey = cex * bey
    bc = bexcey - cexbey
    cexdey = cex * dey
    dexcey = dex * cey
    cd = cexdey - dexcey
    dexaey = dex * aey
    aexdey = aex * dey
    da = dexaey - aexdey
    aexcey = aex * cey
    cexaey = cex * aey
    ac = aexcey - cexaey
    bexdey = bex * dey
    dexbey = dex * bey
    bd = bexdey - dexbey

    alift = aex * aex + aey * aey + aez * aez
    blift = bex * bex + bey * bey + bez * bez
    clift = cex * cex + cey * cey + cez * cez
    dlift = dex * dex + dey * dey + dez * dez

    det = (clift * (dez * ab + aez * bd + bez * da) - dlift * (aez * bc - bez * ac + cez * ab)) + (
        alift * (bez * cd - cez * bd + dez * bc) - blift * (cez * da + dez * ac + aez * cd)
    )

    aezplus = abs(aez)
    bezplus = abs(bez)
    cezplus = abs(cez)
    dezplus = abs(dez)
    aexbeyplus = abs(aexbey) + abs(bexaey)
    bexceyplus = abs(bexcey) + abs(cexbey)
    cexdeyplus = abs(cexdey) + abs(dexcey)
    dexaeyplus = abs(dexaey) + abs(aexdey)
    aexceyplus = abs(aexcey) + abs(cexaey)
    bexdeyplus = abs(bexdey) + abs(dexbey)
    permanent = (
        (cexdeyplus * bezplus + bexdeyplus * cezplus + bexceyplus * dezplus) * alift
        + (dexaeyplus * cezplus + aexceyplus * dezplus + cexdeyplus * aezplus) * blift
        + (aexbeyplus * dezplus + bexdeyplus * aezplus + dexaeyplus * bezplus) * clift
        + (bexceyplus * aezplus + aexceyplus * bezplus + aexbeyplus * cezplus) * dlift
    )

    errbound = isperrboundA * permanent
    if det > errbound or -det > errbound:
        return det
    return -_insphere_mpmath(ax, ay, az, bx, by, bz, cx, cy, cz, dx, dy, dz, ex, ey, ez)


def inspherefast(
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
    ex: float,
    ey: float,
    ez: float,
) -> float:
    aex = ax - ex
    bex = bx - ex
    cex = cx - ex
    dex = dx - ex
    aey = ay - ey
    bey = by - ey
    cey = cy - ey
    dey = dy - ey
    aez = az - ez
    bez = bz - ez
    cez = cz - ez
    dez = dz - ez

    ab = aex * bey - bex * aey
    bc = bex * cey - cex * bey
    cd = cex * dey - dex * cey
    da = dex * aey - aex * dey
    ac = aex * cey - cex * aey
    bd = bex * dey - dex * bey

    abc = aez * bc - bez * ac + cez * ab
    bcd = bez * cd - cez * bd + dez * bc
    cda = cez * da + dez * ac + aez * cd
    dab = dez * ab + aez * bd + bez * da

    alift = aex * aex + aey * aey + aez * aez
    blift = bex * bex + bey * bey + bez * bez
    clift = cex * cex + cey * cey + cez * cez
    dlift = dex * dex + dey * dey + dez * dez

    return (clift * dab - dlift * abc) + (alift * bcd - blift * cda)
