import math


def julian_day(
    year: int, month: int, day: int, hours: float = 0.0, minutes: float = 0.0
) -> float:
    """Convert a Gregorian calendar date to Julian Date (Meeus Ch.7).

    Gregorian-only: the Julian-calendar branch (B = 0) is not implemented,
    so pre-1582 dates are computed as continuous proleptic Gregorian with
    no 1582-10-04 -> 1582-10-15 reform jump (~10 days at the reform,
    century-dependent earlier, vs historical Julian reckoning). Correct
    for prayer use — all operational dates are centuries past the reform —
    and asserted in tests so the limitation is a decision, not a latent quirk.
    """
    if minutes != 0.0:
        hours = hours + (minutes / 60.0)

    Y = year if month > 2 else year - 1
    M = month if month > 2 else month + 12
    D = day + (hours / 24)

    A = math.floor(Y / 100)
    B = math.floor(2 - A + (A / 4))

    i0 = int(365.25 * (Y + 4716))
    i1 = int(30.6001 * (M + 1))

    return i0 + i1 + D + B - 1524.5


def julian_century(JD: float) -> float:
    # Equation from Astronomical Algorithms page 163
    return (JD - 2451545.0) / 36525
