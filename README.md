# adhan-py

[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
![pytest](https://github.com/nexusnv/adhan-py/actions/workflows/test.yml/badge.svg)

This is a port of [batoulapps/adhan-java](https://github.com/batoulapps/adhan-java), a prayer times program, from Java to Python.
As it stands the project reuses most of the structure of the original project but may differ through refactoring and in an effort
to rewrite in a more pythonic way where it makes sense.
Like the original project there are no external dependencies except in development where [pytest](https://github.com/pytest-dev/pytest)
and other development tools are made use of.

## Requirements

* Python >= 3.11

Times are returned as timezone-aware UTC datetimes. Passing a `ZoneInfo`
object converts them on construction; otherwise call `.astimezone(...)`
yourself. On Windows, install the `tzdata` package so `zoneinfo` can
resolve IANA time zones (`pip install tzdata`).

## Limitations

* Polar day/night: above the Arctic circle (or below the Antarctic
  circle) the sun may never rise or set. By default (`NEAREST_LATITUDE`)
  times are estimated at the nearest latitude where it does (Aqrab
  al-Bilad); alternatives are `NEAREST_DAY` (nearest date with a normal
  schedule — returned datetimes carry that date), `MAKKAH` (Makkah's
  schedule), and `NONE` (raise `AstronomicalError` as before). Set via
  `CalculationParameters(polar_circle_rule=...)`. Estimates are
  approximations: near the polar boundary adjacent markers can invert
  by minutes.
* `coordinates` accepts a `(latitude, longitude)` tuple or a
  `Coordinates` object; `date` accepts a `datetime` or a
  `DateComponents` (only the calendar date is used).

## Installation

```
pip install adhan-py
```

## Usage

Create a `PrayerTimes` object by passing geo coodinates, datetime and either passing a calculation method:

```python
prayer_times = PrayerTimes(coordinates, today, CalculationMethod.MOON_SIGHTING_COMMITTEE)
```

Public names are re-exported from the package root, so this also works:

```python
from adhan import PrayerTimes, CalculationMethod, Prayer

prayer_times = PrayerTimes(coordinates, today, CalculationMethod.MOON_SIGHTING_COMMITTEE)
print(prayer_times.time_for_prayer(Prayer.FAJR))
```

Qibla direction (degrees clockwise from north) for a location:

```python
from adhan import Qibla

print(Qibla(coordinates).direction)
```

Sunnah night markers (middle and last third of the night):

```python
from adhan import SunnahTimes

sunnah_times = SunnahTimes(prayer_times)
print(sunnah_times.middle_of_the_night)
print(sunnah_times.last_third_of_the_night)
```

or a calculation parameters object allowing to choose from different parameters such as angles:

```python
parameters = CalculationParameters(fajr_angle=18, isha_angle=18)
prayer_times = PrayerTimes(coordinates, today, calculation_parameters=parameters)
```

If passing a calculation method to the calculation parameters object, the calculation method
will have precedence and will overwrite other parameters you may have also passed.

For instance the MOON_SIGHTING_COMMITTEE method uses a fajr angle of 18 and if for
instance the calculation parameters object is created by passing a different fajr angle the
latter will be ignored:

```python
parameters = CalculationParameters(fajr_angle=12, method=CalculationMethod.MOON_SIGHTING_COMMITTEE)
prayer_times = PrayerTimes(coordinates, today, calculation_parameters=parameters)
print(parameters.fajr_angle)
# 18.0 (the fajr_angle argument has been ignored)
```

Times are returned in UTC time via datetime objects, for convenience it is possible to directly pass
a ZoneInfo object to PrayerTimes:

```python
london_zone = ZoneInfo("Europe/London")
prayer_times = PrayerTimes(
    coordinates,
    today,
    CalculationMethod.MOON_SIGHTING_COMMITTEE,
    time_zone=london_zone,
)

# this will display the time in the chosen time zone
print(f"Fajr: {prayer_times.fajr.strftime('%H:%M')}")
```

or convert to a different timezone later, each prayer time object is in fact a datetime object:

```python
prayer_times = PrayerTimes(
    coordinates,
    today,
    CalculationMethod.MOON_SIGHTING_COMMITTEE,
)

# the following will be in UTC
print(f"Fajr: {prayer_times.fajr.strftime('%H:%M')}")

# and to use a different timezone on the datetime object itself:
london_zone = ZoneInfo("Europe/London")
print(f"Fajr: {prayer_times.fajr.astimezone(london_zone).strftime('%H:%M')}")
```

A full example is located in `src/example` of the project directory.

## Documentation

* [`docs/api.md`](docs/api.md) — full API reference with the per-method parameter table.
* [`docs/migration.md`](docs/migration.md) — migration notes from upstream `1.0.5`.

## Command line

```bash
python -m adhan --latitude 35.7750 --longitude -78.6336 --date 2015-07-12 --method NORTH_AMERICA
```

prints each marker as ISO-8601 UTC (`--date` defaults to today).

## Development

To install adhan-py for development purposes, run the following:

```
python3 -m virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Licence

MIT

## Acknowledgments

Credits go to the author of the original implementation in Java and other languages, especially the very complex astronomy
formulas.
