"""Internals shared by predicates (ported from robust-predicates `esm/util.js`)."""

from __future__ import annotations

epsilon = 1.1102230246251565e-16
splitter = 134217729
resulterrbound = (3 + 8 * epsilon) * epsilon


def sum(elen: int, e: list[float], flen: int, f: list[float], h: list[float]) -> int:
    """fast_expansion_sum_zeroelim — returns new length of h."""
    enow = e[0]
    fnow = f[0]
    eindex = 0
    findex = 0
    if (fnow > enow) == (fnow > -enow):
        Q = enow
        eindex += 1
        if eindex < elen:
            enow = e[eindex]
    else:
        Q = fnow
        findex += 1
        if findex < flen:
            fnow = f[findex]
    hindex = 0
    if eindex < elen and findex < flen:
        if (fnow > enow) == (fnow > -enow):
            Qnew = enow + Q
            hh = Q - (Qnew - enow)
            eindex += 1
            if eindex < elen:
                enow = e[eindex]
        else:
            Qnew = fnow + Q
            hh = Q - (Qnew - fnow)
            findex += 1
            if findex < flen:
                fnow = f[findex]
        Q = Qnew
        if hh != 0:
            h[hindex] = hh
            hindex += 1
        while eindex < elen and findex < flen:
            if (fnow > enow) == (fnow > -enow):
                Qnew = Q + enow
                bvirt = Qnew - Q
                hh = Q - (Qnew - bvirt) + (enow - bvirt)
                eindex += 1
                if eindex < elen:
                    enow = e[eindex]
            else:
                Qnew = Q + fnow
                bvirt = Qnew - Q
                hh = Q - (Qnew - bvirt) + (fnow - bvirt)
                findex += 1
                if findex < flen:
                    fnow = f[findex]
            Q = Qnew
            if hh != 0:
                h[hindex] = hh
                hindex += 1
    while eindex < elen:
        Qnew = Q + enow
        bvirt = Qnew - Q
        hh = Q - (Qnew - bvirt) + (enow - bvirt)
        eindex += 1
        if eindex < elen:
            enow = e[eindex]
        Q = Qnew
        if hh != 0:
            h[hindex] = hh
            hindex += 1
    while findex < flen:
        Qnew = Q + fnow
        bvirt = Qnew - Q
        hh = Q - (Qnew - bvirt) + (fnow - bvirt)
        findex += 1
        if findex < flen:
            fnow = f[findex]
        Q = Qnew
        if hh != 0:
            h[hindex] = hh
            hindex += 1
    if Q != 0 or hindex == 0:
        h[hindex] = Q
        hindex += 1
    return hindex


def estimate(elen: int, e: list[float]) -> float:
    Q = e[0]
    for i in range(1, elen):
        Q += e[i]
    return Q


def sum_three(
    alen: int,
    a: list[float],
    blen: int,
    b: list[float],
    clen: int,
    c: list[float],
    tmp: list[float],
    out: list[float],
) -> int:
    tlen = sum(alen, a, blen, b, tmp)
    return sum(tlen, tmp, clen, c, out)


def scale(elen: int, e: list[float], b: float, h: list[float]) -> int:
    """scale_expansion_zeroelim — returns new length of h."""
    c = splitter * b
    bhi = c - (c - b)
    blo = b - bhi
    enow = e[0]
    Q = enow * b
    c = splitter * enow
    ahi = c - (c - enow)
    alo = enow - ahi
    hh = alo * blo - (Q - ahi * bhi - alo * bhi - ahi * blo)
    hindex = 0
    if hh != 0:
        h[hindex] = hh
        hindex += 1
    for i in range(1, elen):
        enow = e[i]
        product1 = enow * b
        c = splitter * enow
        ahi = c - (c - enow)
        alo = enow - ahi
        product0 = alo * blo - (product1 - ahi * bhi - alo * bhi - ahi * blo)
        sum_ = Q + product0
        bvirt = sum_ - Q
        hh = Q - (sum_ - bvirt) + (product0 - bvirt)
        if hh != 0:
            h[hindex] = hh
            hindex += 1
        Q = product1 + sum_
        hh = sum_ - (Q - product1)
        if hh != 0:
            h[hindex] = hh
            hindex += 1
    if Q != 0 or hindex == 0:
        h[hindex] = Q
        hindex += 1
    return hindex


def negate(elen: int, e: list[float]) -> int:
    for i in range(elen):
        e[i] = -e[i]
    return elen
