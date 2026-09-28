# API reference

All public names are importable from the package root:

```python
from adhanpy import (
    PrayerTimes, Qibla, SunnahTimes,
    CalculationMethod, CalculationParameters,
    HighLatitudeRule, Madhab, PrayerAdjustments,
    Coordinates, Prayer,
)
```

(`adhanpy.astronomy` and `adhanpy.util` are internal implementation
details and not part of the public surface.)

## PrayerTimes

```python
PrayerTimes(coordinates, date, calculation_method=None,
            calculation_parameters=None, time_zone=None)
```

- `coordinates`: `(latitude, longitude)` tuple or `Coordinates`.
- `date`: `datetime` or `DateComponents` — only the calendar date is used.
- Exactly one of `calculation_method` / `calculation_parameters`.
- `time_zone`: optional `ZoneInfo`; times are UTC `datetime`s otherwise.
- Attributes: `fajr`, `sunrise`, `dhuhr`, `asr`, `maghrib`, `isha`
  (timezone-aware `datetime`s).
- Output contract: markers are always non-decreasing
  (`fajr <= sunrise <= dhuhr <= asr <= maghrib <= isha`). Inputs that
  would invert Asr/Dhuhr — polar-boundary geometry, or extreme custom
  `adjustments` — saturate Asr to Dhuhr instead of returning
  inverted times.
- `time_for_prayer(prayer: Prayer) -> datetime` — same values by enum
  (`Prayer.NONE` raises `ConfigurationError`).
- Raises `ConfigurationError` if both/neither of method/parameters is
  given, for a non-`CalculationMethod` method, or for an unknown
  madhab; `AstronomicalError` with details when the sun never
  rises/sets (polar day/night).

## Qibla

```python
Qibla(coordinates).direction  # degrees clockwise from north (float)
```

Accepts a tuple or `Coordinates`, same as `PrayerTimes`.

## SunnahTimes

```python
SunnahTimes(prayer_times).middle_of_the_night       # datetime
SunnahTimes(prayer_times).last_third_of_the_night   # datetime
```

Derived from Maghrib to next-day Fajr. Honors the input's timezone;
UTC arithmetic is used internally so DST transitions are exact.

## CalculationParameters

```python
CalculationParameters(method=None, adjustments=None,
                      method_adjustments=None, isha_interval=0,
                      fajr_angle=0.0, isha_angle=0.0)
```

- `madhab`: `Madhab.SHAFI` (default) or `Madhab.HANAFI` (later Asr).
- `high_latitude_rule`: `MIDDLE_OF_THE_NIGHT` (default),
  `SEVENTH_OF_THE_NIGHT`, or `TWILIGHT_ANGLE`.
- `adjustments` / `method_adjustments`: `PrayerAdjustments` minute
  offsets (per-instance; never shared between instances).
- A `method` overwrites the angles/interval/adjustments it defines;
  with `CalculationMethod.NONE` (default) everything stays manual.

## Calculation methods

| Method | Fajr angle | Isha angle / interval | Built-in offsets |
| --- | ---: | --- | --- |
| `MUSLIM_WORLD_LEAGUE` | 18 | 17 | dhuhr +1 |
| `EGYPTIAN` | 19.5 | 17.5 | dhuhr +1 |
| `KARACHI` | 18 | 18 | dhuhr +1 |
| `UMM_AL_QURA` | 18.5 | +90 min after Maghrib | — |
| `DUBAI` | 18.2 | 18.2 | sunrise −3, dhuhr/asr/maghrib +3 |
| `MOON_SIGHTING_COMMITTEE` | 18 | 18 | dhuhr +5, maghrib +3 (+ seasonal twilight tables, lat ≥ 55 rules) |
| `NORTH_AMERICA` | 15 | 15 | dhuhr +1 |
| `KUWAIT` | 18 | 17.5 | — |
| `QATAR` | 18 | +90 min after Maghrib | — |
| `SINGAPORE` | 20 | 18 | dhuhr +1 |
| `UOIF` | 12 | 12 | — |
| `NONE` | manual | manual | — |

## Value types

- `Coordinates(latitude, longitude)` — dataclass of floats.
- `PolarCircleRule` — `NEAREST_LATITUDE` (default), `NEAREST_DAY`,
  `MAKKAH`, `NONE`; estimation strategy for polar day/night, set via
  `CalculationParameters(polar_circle_rule=...)`.
- `Prayer` — `FAJR, SUNRISE, DHUHR, ASR, MAGHRIB, ISHA` (`NONE` sentinel).
- `PrayerAdjustments(fajr=0, sunrise=0, dhuhr=0, asr=0, maghrib=0, isha=0)` — minute offsets.
- `NightPortions(fajr, isha)` — fractions from `night_portions()`.
- `ShadowLength` — `SINGLE` (1.0, Shafi) / `DOUBLE` (2.0, Hanafi) wrapper.

## CLI

```bash
python -m adhanpy --latitude 35.7750 --longitude -78.6336 \
  --date 2015-07-12 --method NORTH_AMERICA
```

Prints `name=ISO-8601` lines in UTC (`--date` defaults to today).

## Errors

`AdhanError` is the base for all library errors (importable from the
`adhanpy` root). Subclasses: `AstronomicalError` (polar day/night,
undefined Asr), `ConfigurationError` (bad method/madhab/polar rule/
prayer/high-latitude rule, method-vs-parameters exclusivity),
`ValidationError` (out-of-range coordinates, angles, intervals).
The isha-interval `ValueError` is internal control-flow and unchanged.
