"""Ellipsoidal geodesics on WGS84 (Karney inverse, vendored).

Vendored subset of GeographicLib 2.1 (``geodesic.py`` / ``geomath.py`` /
``geodesiccapability.py``) by Charles F. F. Karney, MIT/X11 licensed::

    Copyright (c) Charles Karney (2011-2022) <karney@alum.mit.edu>

Algorithms derived in C. F. F. Karney, "Algorithms for geodesics",
*J. Geodesy* 87, 43-55 (2013), https://doi.org/10.1007/s00190-012-0578-z.

Vincenty (1975) is deliberately omitted: its iteration is documented
non-convergent for nearly-antipodal points, while Karney's hybrid
Newton/astroid iteration converges for all inputs.

What was kept: the inverse-problem path only (series helpers A1/C1/A2/C2/A3/C3,
``_lengths``, ``_inverse_start``, ``_lambda12``, ``_gen_inverse``) plus the small
angle helpers from ``geomath.py``. Direct/line/polygon/area machinery
(C1', C4, geodesic tables) is omitted. Logic is unchanged from upstream;
formatting and type annotations are ours (stdlib ``math`` only).
"""

import math
import numbers
import sys
from collections.abc import Sequence
from decimal import Decimal

from alfalak.exceptions import AstronomicalError, ValidationError

# ---------------------------------------------------------------------------
# WGS84 defining constants (exact) and derived quantities (labeled as such).
# Ref: NGA WGS-84 manual; a and 1/f are defining, b and e^2 are derived.
# ---------------------------------------------------------------------------

WGS84_A: float = 6378137.0
"""WGS84 equatorial radius in metres (defining, exact)."""

WGS84_F: float = 1 / 298.257223563
"""WGS84 flattening (defining, exact)."""

WGS84_B: float = WGS84_A * (1 - WGS84_F)
"""WGS84 polar semi-axis in metres (derived as a * (1 - f); NGA: 6356752.31424518)."""

WGS84_E2: float = WGS84_F * (2 - WGS84_F)
"""WGS84 first eccentricity squared (derived as f * (2 - f); NGA: 0.00669437999014)."""

_F1: float = 1 - WGS84_F
_E2: float = WGS84_F * (2 - WGS84_F)
_EP2: float = _E2 / (_F1 * _F1)
_N: float = WGS84_F / (2 - WGS84_F)
_B: float = WGS84_B

# Series order (GEOGRAPHICLIB_GEODESIC_ORDER in upstream).
_N_A1: int = 6
_N_C1: int = 6
_N_A2: int = 6
_N_C2: int = 6
_N_A3: int = 6
_N_A3X: int = 6
_N_C3: int = 6
_N_C3X: int = 15

_MAXIT1: int = 20
_MAXIT2: int = _MAXIT1 + sys.float_info.mant_dig + 10

_TINY: float = math.sqrt(sys.float_info.min)
_TOL0: float = sys.float_info.epsilon
_TOL1: float = 200 * _TOL0
_TOL2: float = math.sqrt(_TOL0)
_TOLB: float = _TOL0
_XTHRESH: float = 1000 * _TOL2
_ETOL2: float = (
    0.1 * _TOL2 / math.sqrt(max(0.001, abs(WGS84_F)) * min(1.0, 1 - WGS84_F / 2) / 2)
)

# Output-mask bits (values from upstream geodesiccapability.py; the inverse
# below always runs with _OUTMASK = AZIMUTH | DISTANCE).
_MASK_EMPTY: int = 0
_MASK_AZIMUTH: int = 1 << 9
_MASK_DISTANCE: int = (1 << 10) | 1
_MASK_REDUCEDLENGTH: int = (1 << 12) | 1 | (1 << 2)
_MASK_GEODESICSCALE: int = (1 << 13) | 1 | (1 << 2)
_MASK_OUT: int = 0xFF80
_OUTMASK: int = _MASK_AZIMUTH | _MASK_DISTANCE


def _a3_coeff() -> list[float]:
    coeff = [-3, 128, -2, -3, 64, -1, -3, -1, 16, 3, -1, -2, 8, 1, -1, 2, 1, 1]
    table = [0.0] * _N_A3X
    o = 0
    k = 0
    for j in range(_N_A3 - 1, -1, -1):
        m = min(_N_A3 - j - 1, j)
        table[k] = _polyval(m, coeff, o, _N) / coeff[o + m + 1]
        k += 1
        o += m + 2
    return table


def _c3_coeff() -> list[float]:
    coeff = [
        3,
        128,
        2,
        5,
        128,
        -1,
        3,
        3,
        64,
        -1,
        0,
        1,
        8,
        -1,
        1,
        4,
        5,
        256,
        1,
        3,
        128,
        -3,
        -2,
        3,
        64,
        1,
        -3,
        2,
        32,
        7,
        512,
        -10,
        9,
        384,
        5,
        -9,
        5,
        192,
        7,
        512,
        -14,
        7,
        512,
        21,
        2560,
    ]
    table = [0.0] * _N_C3X
    o = 0
    k = 0
    for lev in range(1, _N_C3):
        for j in range(_N_C3 - 1, lev - 1, -1):
            m = min(_N_C3 - j - 1, j)
            table[k] = _polyval(m, coeff, o, _N) / coeff[o + m + 1]
            k += 1
            o += m + 2
    return table


_A3X: list[float]
_C3X: list[float]


# ---------------------------------------------------------------------------
# Small angle helpers (from upstream geomath.py).
# ---------------------------------------------------------------------------


def _sq(x: float) -> float:
    return x * x


def _cbrt(x: float) -> float:
    return math.copysign(math.pow(abs(x), 1 / 3.0), x)


def _norm(x: float, y: float) -> tuple[float, float]:
    r = math.hypot(x, y)
    return x / r, y / r


def _esum(u: float, v: float) -> tuple[float, float]:
    s = u + v
    up = s - v
    vpp = s - up
    up -= u
    vpp -= v
    t = s if s == 0 else 0.0 - (up + vpp)
    return s, t


def _polyval(n: int, p: Sequence[float], s: int, x: float) -> float:
    y = float(0 if n < 0 else p[s])
    while n > 0:
        n -= 1
        s += 1
        y = y * x + p[s]
    return y


def _ang_round(x: float) -> float:
    z = 1 / 16.0
    y = abs(x)
    if y < z:
        y = z - (z - y)
    return math.copysign(y, x)


def _ang_diff(x: float, y: float) -> tuple[float, float]:
    d, t = _esum(math.remainder(-x, 360), math.remainder(y, 360))
    d, t = _esum(math.remainder(d, 360), t)
    if d == 0 or abs(d) == 180:
        d = math.copysign(d, y - x if t == 0 else -t)
    return d, t


def _sincosd(x: float) -> tuple[float, float]:
    r = math.fmod(x, 360) if math.isfinite(x) else math.nan
    q = 0 if math.isnan(r) else int(round(r / 90))
    r -= 90 * q
    r = math.radians(r)
    s = math.sin(r)
    c = math.cos(r)
    q = q % 4
    if q == 1:
        s, c = c, -s
    elif q == 2:
        s, c = -s, -c
    elif q == 3:
        s, c = -c, s
    c = c + 0.0
    if s == 0:
        s = math.copysign(s, x)
    return s, c


def _sincosde(x: float, t: float) -> tuple[float, float]:
    q = int(round(x / 90)) if math.isfinite(x) else 0
    r = x - 90 * q
    r = math.radians(_ang_round(r + t))
    s = math.sin(r)
    c = math.cos(r)
    q = q % 4
    if q == 1:
        s, c = c, -s
    elif q == 2:
        s, c = -s, -c
    elif q == 3:
        s, c = -c, s
    c = c + 0.0
    if s == 0:
        s = math.copysign(s, x)
    return s, c


def _atan2d(y: float, x: float) -> float:
    if abs(y) > abs(x):
        q = 2
        x, y = y, x
    else:
        q = 0
    if x < 0:
        q += 1
        x = -x
    ang = math.degrees(math.atan2(y, x))
    if q == 1:
        ang = math.copysign(180, y) - ang
    elif q == 2:
        ang = 90 - ang
    elif q == 3:
        ang = -90 + ang
    return ang


# ---------------------------------------------------------------------------
# Trigonometric series (from upstream geodesic.py).
# ---------------------------------------------------------------------------


def _sincos_series(sinx: float, cosx: float, c: Sequence[float]) -> float:
    # Sin-series only (upstream also has a cos branch used solely by the
    # omitted area computation). Clenshaw summation, unchanged.
    k = len(c)
    n = k - 1
    ar = 2 * (cosx - sinx) * (cosx + sinx)
    y1 = 0.0
    if n & 1:
        k -= 1
        y0 = c[k]
    else:
        y0 = 0.0
    n = n // 2
    while n:
        n -= 1
        k -= 1
        y1 = ar * y0 - y1 + c[k]
        k -= 1
        y0 = ar * y1 - y0 + c[k]
    return 2 * sinx * cosx * y0


def _astroid(x: float, y: float) -> float:
    p = _sq(x)
    q = _sq(y)
    r = (p + q - 1) / 6
    if not (q == 0 and r <= 0):
        s = p * q / 4
        r2 = _sq(r)
        r3 = r * r2
        disc = s * (s + 2 * r3)
        u = r
        if disc >= 0:
            t3 = s + r3
            t3 += -math.sqrt(disc) if t3 < 0 else math.sqrt(disc)
            t = _cbrt(t3)
            u += t + (r2 / t if t != 0 else 0)
        else:
            ang = math.atan2(math.sqrt(-disc), -(s + r3))
            u += 2 * r * math.cos(ang / 3)
        v = math.sqrt(_sq(u) + q)
        uv = q / (v - u) if u < 0 else u + v
        w = (uv - q) / (2 * v)
        k = uv / (math.sqrt(uv + _sq(w)) + w)
    else:
        k = 0.0
    return k


def _a1m1f(eps: float) -> float:
    coeff = [1, 4, 64, 0, 256]
    m = _N_A1 // 2
    t = _polyval(m, coeff, 0, _sq(eps)) / coeff[m + 1]
    return (t + eps) / (1 - eps)


def _c1f(eps: float, c: list[float]) -> None:
    coeff = [
        -1,
        6,
        -16,
        32,
        -9,
        64,
        -128,
        2048,
        9,
        -16,
        768,
        3,
        -5,
        512,
        -7,
        1280,
        -7,
        2048,
    ]
    eps2 = _sq(eps)
    d = eps
    o = 0
    for lev in range(1, _N_C1 + 1):
        m = (_N_C1 - lev) // 2
        c[lev] = d * _polyval(m, coeff, o, eps2) / coeff[o + m + 1]
        o += m + 2
        d *= eps


def _a2m1f(eps: float) -> float:
    coeff = [-11, -28, -192, 0, 256]
    m = _N_A2 // 2
    t = _polyval(m, coeff, 0, _sq(eps)) / coeff[m + 1]
    return (t - eps) / (1 + eps)


def _c2f(eps: float, c: list[float]) -> None:
    coeff = [
        1,
        2,
        16,
        32,
        35,
        64,
        384,
        2048,
        15,
        80,
        768,
        7,
        35,
        512,
        63,
        1280,
        77,
        2048,
    ]
    eps2 = _sq(eps)
    d = eps
    o = 0
    for lev in range(1, _N_C2 + 1):
        m = (_N_C2 - lev) // 2
        c[lev] = d * _polyval(m, coeff, o, eps2) / coeff[o + m + 1]
        o += m + 2
        d *= eps


def _a3f(eps: float) -> float:
    return _polyval(_N_A3 - 1, _A3X, 0, eps)


def _c3f(eps: float, c: list[float]) -> None:
    mult = 1.0
    o = 0
    for lev in range(1, _N_C3):
        m = _N_C3 - lev - 1
        mult *= eps
        c[lev] = mult * _polyval(m, _C3X, o, eps)
        o += m + 1


_A3X = _a3_coeff()
_C3X = _c3_coeff()


def _lengths(
    eps: float,
    sig12: float,
    ssig1: float,
    csig1: float,
    dn1: float,
    ssig2: float,
    csig2: float,
    dn2: float,
    cbet1: float,
    cbet2: float,
    outmask: int,
    c1a: list[float],
    c2a: list[float],
) -> tuple[float, float, float, float, float]:
    outmask &= _MASK_OUT
    s12b = m12b = m0 = m0x = j12 = m12 = m21 = math.nan
    if outmask & (_MASK_DISTANCE | _MASK_REDUCEDLENGTH):
        a1 = _a1m1f(eps)
        _c1f(eps, c1a)
        if outmask & (_MASK_REDUCEDLENGTH):
            a2 = _a2m1f(eps)
            _c2f(eps, c2a)
            m0x = a1 - a2
            a2 = 1 + a2
        a1 = 1 + a1
    if outmask & _MASK_DISTANCE:
        b1 = _sincos_series(ssig2, csig2, c1a) - _sincos_series(ssig1, csig1, c1a)
        s12b = a1 * (sig12 + b1)
        if outmask & (_MASK_REDUCEDLENGTH):
            b2 = _sincos_series(ssig2, csig2, c2a) - _sincos_series(ssig1, csig1, c2a)
            j12 = m0x * sig12 + (a1 * b1 - a2 * b2)
    elif outmask & (_MASK_REDUCEDLENGTH):
        for lev in range(1, _N_C2):
            c2a[lev] = a1 * c1a[lev] - a2 * c2a[lev]
        j12 = m0x * sig12 + (
            _sincos_series(ssig2, csig2, c2a) - _sincos_series(ssig1, csig1, c2a)
        )
    if outmask & _MASK_REDUCEDLENGTH:
        m0 = m0x
        m12b = dn2 * (csig1 * ssig2) - dn1 * (ssig1 * csig2) - csig1 * csig2 * j12
    # (Geodesic-scale outputs omitted: no caller requests GEODESICSCALE.)
    return s12b, m12b, m0, m12, m21


def _inverse_start(
    sbet1: float,
    cbet1: float,
    dn1: float,
    sbet2: float,
    cbet2: float,
    dn2: float,
    lam12: float,
    slam12: float,
    clam12: float,
    c1a: list[float],
    c2a: list[float],
) -> tuple[float, float, float, float, float, float]:
    sig12 = -1.0
    salp2 = calp2 = dnm = math.nan
    sbet12 = sbet2 * cbet1 - cbet2 * sbet1
    cbet12 = cbet2 * cbet1 + sbet2 * sbet1
    sbet12a = sbet2 * cbet1
    sbet12a += cbet2 * sbet1

    shortline = cbet12 >= 0 and sbet12 < 0.5 and cbet2 * lam12 < 0.5
    if shortline:
        sbetm2 = _sq(sbet1 + sbet2)
        sbetm2 /= sbetm2 + _sq(cbet1 + cbet2)
        dnm = math.sqrt(1 + _EP2 * sbetm2)
        omg12 = lam12 / (_F1 * dnm)
        somg12 = math.sin(omg12)
        comg12 = math.cos(omg12)
    else:
        somg12 = slam12
        comg12 = clam12

    salp1 = cbet2 * somg12
    if comg12 >= 0:
        calp1 = sbet12 + cbet2 * sbet1 * _sq(somg12) / (1 + comg12)
    else:
        calp1 = sbet12a - cbet2 * sbet1 * _sq(somg12) / (1 - comg12)

    ssig12 = math.hypot(salp1, calp1)
    csig12 = sbet1 * sbet2 + cbet1 * cbet2 * comg12

    if shortline and ssig12 < _ETOL2:
        salp2 = cbet1 * somg12
        if comg12 >= 0:
            calp2 = sbet12 - cbet1 * sbet2 * (_sq(somg12) / (1 + comg12))
        else:
            calp2 = sbet12 - cbet1 * sbet2 * (1 - comg12)
        salp2, calp2 = _norm(salp2, calp2)
        sig12 = math.atan2(ssig12, csig12)
    elif abs(_N) >= 0.1 or csig12 >= 0 or ssig12 >= 6 * abs(_N) * math.pi * _sq(cbet1):
        pass
    else:
        lam12x = math.atan2(-slam12, -clam12)
        k2 = _sq(sbet1) * _EP2
        eps = k2 / (2 * (1 + math.sqrt(1 + k2)) + k2)
        lamscale = WGS84_F * cbet1 * _a3f(eps) * math.pi
        betscale = lamscale * cbet1
        x = lam12x / lamscale
        y = sbet12a / betscale

        if y > -_TOL1 and x > -1 - _XTHRESH:
            salp1 = min(1.0, -x)
            calp1 = -math.sqrt(1 - _sq(salp1))
        else:
            k = _astroid(x, y)
            omg12a = lamscale * (-x * k / (1 + k))
            somg12 = math.sin(omg12a)
            comg12 = -math.cos(omg12a)
            salp1 = cbet2 * somg12
            calp1 = sbet12a - cbet2 * sbet1 * _sq(somg12) / (1 - comg12)
    if not salp1 <= 0:
        salp1, calp1 = _norm(salp1, calp1)
    else:
        salp1 = 1.0
        calp1 = 0.0
    return sig12, salp1, calp1, salp2, calp2, dnm


def _lambda12(
    sbet1: float,
    cbet1: float,
    dn1: float,
    sbet2: float,
    cbet2: float,
    dn2: float,
    salp1: float,
    calp1: float,
    slam120: float,
    clam120: float,
    diffp: bool,
    c1a: list[float],
    c2a: list[float],
    c3a: list[float],
) -> tuple[float, float, float, float, float, float, float, float, float, float, float]:
    if sbet1 == 0 and calp1 == 0:
        calp1 = -_TINY

    salp0 = salp1 * cbet1
    calp0 = math.hypot(calp1, salp1 * sbet1)

    ssig1 = sbet1
    somg1 = salp0 * sbet1
    csig1 = comg1 = calp1 * cbet1
    ssig1, csig1 = _norm(ssig1, csig1)

    if cbet2 != cbet1:
        salp2 = salp0 / cbet2
    else:
        salp2 = salp1
    if cbet2 != cbet1 or abs(sbet2) != -sbet1:
        calp2 = (
            math.sqrt(
                _sq(calp1 * cbet1)
                + (
                    (cbet2 - cbet1) * (cbet1 + cbet2)
                    if cbet1 < -sbet1
                    else (sbet1 - sbet2) * (sbet1 + sbet2)
                )
            )
            / cbet2
        )
    else:
        calp2 = abs(calp1)
    ssig2 = sbet2
    somg2 = salp0 * sbet2
    csig2 = comg2 = calp2 * cbet2
    ssig2, csig2 = _norm(ssig2, csig2)

    sig12 = math.atan2(
        max(0.0, csig1 * ssig2 - ssig1 * csig2) + 0.0, csig1 * csig2 + ssig1 * ssig2
    )

    somg12 = max(0.0, comg1 * somg2 - somg1 * comg2) + 0.0
    comg12 = comg1 * comg2 + somg1 * somg2
    eta = math.atan2(
        somg12 * clam120 - comg12 * slam120, comg12 * clam120 + somg12 * slam120
    )

    k2 = _sq(calp0) * _EP2
    eps = k2 / (2 * (1 + math.sqrt(1 + k2)) + k2)
    _c3f(eps, c3a)
    b312 = _sincos_series(ssig2, csig2, c3a) - _sincos_series(ssig1, csig1, c3a)
    domg12 = -WGS84_F * _a3f(eps) * salp0 * (sig12 + b312)
    lam12 = eta + domg12

    if diffp:
        if calp2 == 0:
            dlam12 = -2 * _F1 * dn1 / sbet1
        else:
            _, dlam12, _, _, _ = _lengths(
                eps,
                sig12,
                ssig1,
                csig1,
                dn1,
                ssig2,
                csig2,
                dn2,
                cbet1,
                cbet2,
                _MASK_REDUCEDLENGTH,
                c1a,
                c2a,
            )
            dlam12 *= _F1 / (calp2 * cbet2)
    else:
        dlam12 = math.nan

    return (
        lam12,
        salp2,
        calp2,
        sig12,
        ssig1,
        csig1,
        ssig2,
        csig2,
        eps,
        domg12,
        dlam12,
    )


def _gen_inverse(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> tuple[float, float, float, float, float, float, float, float, float, float]:
    outmask = _OUTMASK & _MASK_OUT
    a12 = s12 = m12 = m12_out = m21 = s_area = math.nan
    orig = (lat1, lon1, lat2, lon2)

    lon12, lon12s = _ang_diff(lon1, lon2)
    lonsign = math.copysign(1, lon12)
    lon12 = lonsign * lon12
    lon12s = lonsign * lon12s
    lam12 = math.radians(lon12)
    slam12, clam12 = _sincosde(lon12, lon12s)
    lon12s = (180 - lon12) - lon12s

    lat1 = _ang_round(lat1 if abs(lat1) <= 90 else math.nan)
    lat2 = _ang_round(lat2 if abs(lat2) <= 90 else math.nan)
    swapp = -1 if abs(lat1) < abs(lat2) or math.isnan(lat2) else 1
    if swapp < 0:
        lonsign *= -1
        lat2, lat1 = lat1, lat2
    latsign = math.copysign(1, -lat1)
    lat1 *= latsign
    lat2 *= latsign

    sbet1, cbet1 = _sincosd(lat1)
    sbet1 *= _F1
    sbet1, cbet1 = _norm(sbet1, cbet1)
    cbet1 = max(_TINY, cbet1)

    sbet2, cbet2 = _sincosd(lat2)
    sbet2 *= _F1
    sbet2, cbet2 = _norm(sbet2, cbet2)
    cbet2 = max(_TINY, cbet2)

    if cbet1 < -sbet1:
        if cbet2 == cbet1:
            sbet2 = math.copysign(sbet1, sbet2)
    else:
        if abs(sbet2) == -sbet1:
            cbet2 = cbet1

    dn1 = math.sqrt(1 + _EP2 * _sq(sbet1))
    dn2 = math.sqrt(1 + _EP2 * _sq(sbet2))

    c1a = [0.0] * (_N_C1 + 1)
    c2a = [0.0] * (_N_C2 + 1)
    c3a = [0.0] * _N_C3

    meridian = lat1 == -90 or slam12 == 0

    if meridian:
        calp1 = clam12
        salp1 = slam12
        calp2 = 1.0
        salp2 = 0.0

        ssig1 = sbet1
        csig1 = calp1 * cbet1
        ssig2 = sbet2
        csig2 = calp2 * cbet2

        sig12 = math.atan2(
            max(0.0, csig1 * ssig2 - ssig1 * csig2) + 0.0,
            csig1 * csig2 + ssig1 * ssig2,
        )

        s12x, m12x, _, m12_out, m21 = _lengths(
            _N,
            sig12,
            ssig1,
            csig1,
            dn1,
            ssig2,
            csig2,
            dn2,
            cbet1,
            cbet2,
            outmask | _MASK_DISTANCE | _MASK_REDUCEDLENGTH,
            c1a,
            c2a,
        )

        if sig12 < _TOL2 or m12x >= 0:
            if sig12 < 3 * _TINY or (sig12 < _TOL0 and (s12x < 0 or m12x < 0)):
                sig12 = m12x = s12x = 0.0
            m12x *= _B
            s12x *= _B
            a12 = math.degrees(sig12)
        else:
            meridian = False

    # (Area machinery omitted: this module solves azimuth + distance only.)

    if not meridian and sbet1 == 0 and (WGS84_F <= 0 or lon12s >= WGS84_F * 180):
        calp1 = calp2 = 0.0
        salp1 = salp2 = 1.0
        s12x = WGS84_A * lam12
        sig12 = lam12 / _F1
        m12x = _B * math.sin(sig12)
        a12 = lon12 / _F1

    elif not meridian:
        sig12, salp1, calp1, salp2, calp2, dnm = _inverse_start(
            sbet1, cbet1, dn1, sbet2, cbet2, dn2, lam12, slam12, clam12, c1a, c2a
        )

        if sig12 >= 0:
            s12x = sig12 * _B * dnm
            m12x = _sq(dnm) * _B * math.sin(sig12 / dnm)
            a12 = math.degrees(sig12)
        else:
            numit = 0
            tripn = tripb = False
            salp1a = _TINY
            calp1a = 1.0
            salp1b = _TINY
            calp1b = -1.0
            converged = False

            while True:
                (
                    v,
                    salp2,
                    calp2,
                    sig12,
                    ssig1,
                    csig1,
                    ssig2,
                    csig2,
                    eps,
                    domg12,
                    dv,
                ) = _lambda12(
                    sbet1,
                    cbet1,
                    dn1,
                    sbet2,
                    cbet2,
                    dn2,
                    salp1,
                    calp1,
                    slam12,
                    clam12,
                    numit < _MAXIT1,
                    c1a,
                    c2a,
                    c3a,
                )
                if tripb or abs(v) < (8 if tripn else 1) * _TOL0:
                    converged = True
                    break
                if numit == _MAXIT2:
                    break
                if v > 0 and (numit > _MAXIT1 or calp1 / salp1 > calp1b / salp1b):
                    salp1b = salp1
                    calp1b = calp1
                elif v < 0 and (numit > _MAXIT1 or calp1 / salp1 < calp1a / salp1a):
                    salp1a = salp1
                    calp1a = calp1

                numit += 1
                if numit < _MAXIT1 and dv > 0:
                    dalp1 = -v / dv
                    if abs(dalp1) < math.pi:
                        sdalp1 = math.sin(dalp1)
                        cdalp1 = math.cos(dalp1)
                        nsalp1 = salp1 * cdalp1 + calp1 * sdalp1
                        if nsalp1 > 0:
                            calp1 = calp1 * cdalp1 - salp1 * sdalp1
                            salp1 = nsalp1
                            salp1, calp1 = _norm(salp1, calp1)
                            tripn = abs(v) <= 16 * _TOL0
                            continue
                salp1 = (salp1a + salp1b) / 2
                calp1 = (calp1a + calp1b) / 2
                salp1, calp1 = _norm(salp1, calp1)
                tripn = False
                tripb = (
                    abs(salp1a - salp1) + (calp1a - calp1) < _TOLB
                    or abs(salp1 - salp1b) + (calp1 - calp1b) < _TOLB
                )

            if not converged:
                raise AstronomicalError(
                    "Ellipsoidal inverse failed to converge for "
                    f"{orig[0]}, {orig[1]} -> {orig[2]}, {orig[3]}; this "
                    "indicates a numerical bug, since Karney converges "
                    "for all inputs."
                )

            lengthmask = outmask | (
                _MASK_DISTANCE if (outmask & (_MASK_REDUCEDLENGTH)) else _MASK_EMPTY
            )
            s12x, m12x, _, m12_out, m21 = _lengths(
                eps,
                sig12,
                ssig1,
                csig1,
                dn1,
                ssig2,
                csig2,
                dn2,
                cbet1,
                cbet2,
                lengthmask,
                c1a,
                c2a,
            )

            m12x *= _B
            s12x *= _B
            a12 = math.degrees(sig12)

    # Fixed outmask is always AZIMUTH | DISTANCE: s12 is always computed,
    # reduced-length/scale outputs are never requested.
    s12 = 0.0 + s12x

    if swapp < 0:
        salp2, salp1 = salp1, salp2
        calp2, calp1 = calp1, calp2

    salp1 *= swapp * lonsign
    calp1 *= swapp * latsign
    salp2 *= swapp * lonsign
    calp2 *= swapp * latsign

    return a12, s12, salp1, calp1, salp2, calp2, m12, m12_out, m21, s_area


def geodesic_inverse(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> tuple[float, float]:
    """Solve the inverse geodesic problem on the WGS84 ellipsoid.

    :param lat1: latitude of the first point in degrees, within [-90, 90].
    :param lon1: longitude of the first point in degrees, within [-180, 180].
    :param lat2: latitude of the second point in degrees, within [-90, 90].
    :param lon2: longitude of the second point in degrees, within [-180, 180].
    :return: ``(forward_azimuth_deg, distance_m)`` — forward azimuth is in
        (-180, 180] (east positive, matching GeographicLib convention);
        distance is in metres, never NaN.

    Raises :class:`ValidationError` for out-of-range/non-finite/non-numeric
    input (booleans rejected, mirroring ``Coordinates``) and
    :class:`AstronomicalError` if the iteration fails to converge (defensive:
    Karney converges for all inputs on WGS84).
    """
    for name, value in (("lat1", lat1), ("lat2", lat2)):
        if isinstance(value, bool) or not isinstance(value, (numbers.Real, Decimal)):
            raise ValidationError(
                f"Latitude must be a real number, got {value!r} ({name})."
            )
        if not math.isfinite(value) or not -90.0 <= value <= 90.0:
            raise ValidationError(
                f"Latitude must be within [-90.0, 90.0], got {value!r} ({name})."
            )
    for name, value in (("lon1", lon1), ("lon2", lon2)):
        if isinstance(value, bool) or not isinstance(value, (numbers.Real, Decimal)):
            raise ValidationError(
                f"Longitude must be a real number, got {value!r} ({name})."
            )
        if not math.isfinite(value) or not -180.0 <= value <= 180.0:
            raise ValidationError(
                f"Longitude must be within [-180.0, 180.0], got {value!r} ({name})."
            )
    _, s12, salp1, calp1, _, _, _, _, _, _ = _gen_inverse(
        float(lat1), float(lon1), float(lat2), float(lon2)
    )
    azi = _atan2d(salp1, calp1)
    if azi == -180.0:
        azi = 180.0
    else:
        azi = azi + 0.0  # normalize -0.0 to +0.0
    return azi, s12
