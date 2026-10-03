---
title: Calculation Methods
description: Compare all supported prayer time calculation methods.
---

# Calculation Methods

Al-Falak supports 12 calculation methods. Each method defines Fajr and Isha angles (or intervals) and may include additional adjustments.

## Method comparison

| Method | Fajr Angle | Isha Angle | Isha Interval | Notes |
|---|---|---|---|---|
| Muslim World League | 18° | 17° | — | Standard MWL method |
| ISNA (North America) | 15° | 15° | — | Not recommended for general use |
| Egyptian | 19.5° | 17.5° | — | Egyptian General Authority |
| Karachi | 18° | 18° | — | University of Islamic Sciences |
| Umm al-Qura | 18.5° | — | 90 min | Add +30 min in Ramadan |
| Dubai | 18.2° | 18.2° | — | Gulf region |
| Moonsighting Committee | 18° | 18° | — | Seasonal adjustments |
| Kuwait | 18° | 17.5° | — | Kuwait method |
| Qatar | 18° | — | 90 min | Modified Umm al-Qura |
| Singapore | 20° | 18° | — | Singapore method |
| UOIF | 12° | 12° | — | Union des organisations islamiques de France |
| JAKIM | 20° | 18° | — | Malaysia (JAKIM); same 20/18 computation as Singapore |

## JAKIM preset

`JAKIM` uses Fajr 20° and Isha 18° with `dhuhr +1`, identical to `SINGAPORE`
by design. It is not a different twilight computation: the separate preset
exists for Malaysian operations (Malay naming, Malaysian zone handling, and
e-solat timetable alignment).

Verification anchors (checked 2026-10-03): Kuala Lumpur (3.1390, 101.6869)
and Kota Kinabalu (5.9804, 116.0735) on 2025-01-15 lock the computed 20/18
baseline in `tests/test_prayer_times.py`, with `JAKIM == SINGAPORE` asserted
to the second. Official e-solat tables may add minute-level administrative
adjustments on top of this baseline.

## Imsak

`Imsak = Fajr - imsak_offset` (default 10 minutes, configurable via
`CalculationParameters(imsak_offset=...)`). The JAKIM convention defaults to
10, but published Malaysian tables are mostly — not always — exactly Fajr-10,
so the offset stays configurable rather than hardcoded. The offset applies to
the rounded Fajr (equivalent to pre-rounding for integer-minute offsets);
`adjustments.imsak` applies on top, and Fajr adjustments flow through to
Imsak. Defined for all methods including `NONE`.

## Provenance notes

- Dubai: the 18.2°/18.2° angles plus `sunrise -3, dhuhr +3, asr +3, maghrib +3`
  minute offsets are app-level tuning carried over from BatoulApps research,
  not an official IACAD/Awqaf specification. Treat them as conventional, not
  authoritative.
- Qatar: this preset follows the library-canonical 18° + 90-minute Isha
  definition. Some current Doha Awqaf publications cite 18.5° + 90 minutes;
  that conflict is recorded here and left unresolved pending a primary source.

## Using a method

```python
from alfalak import PrayerTimes, CalculationMethod

prayer_times = PrayerTimes(
    coordinates,
    datetime.now(),
    CalculationMethod.MUSLIM_WORLD_LEAGUE,
)
```

## Custom parameters

Override any method's defaults with `CalculationParameters`:

```python
from alfalak import CalculationParameters

params = CalculationParameters(
    fajr_angle=18,
    isha_angle=17,
    isha_interval=0,
)
```

## Method precedence

When you pass both a `CalculationMethod` and custom parameters to `CalculationParameters`, the method's built-in values take precedence:

```python
# fajr_angle=12 is ignored because MOON_SIGHTING_COMMITTEE sets it to 18
params = CalculationParameters(
    fajr_angle=12,
    method=CalculationMethod.MOON_SIGHTING_COMMITTEE,
)
print(params.fajr_angle)  # 18.0
```

## See also

- [Madhab](/madhab/) — Shafi vs Hanafi Asr calculation
- [High Latitude Rules](/high-latitude/) — handling extreme latitudes
- [Polar Regions](/polar-regions/) — handling polar day/night
