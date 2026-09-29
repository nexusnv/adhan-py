# adhan-py

[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
![pytest](https://github.com/nexusnv/adhan-py/actions/workflows/test.yml/badge.svg)

An offline Python library for calculating Islamic prayer times. A community-maintained fork of [alphahm/adhanpy](https://github.com/alphahm/adhanpy), which is a Python port of [batoulapps/adhan](https://github.com/batoulapps/adhan) (Java).

Part of the `adhan` family of libraries:

| Language | Package |
|---|---|
| JavaScript | [`adhan`](https://github.com/batoulapps/adhan-js) |
| Swift | [`adhan-swift`](https://github.com/batoulapps/adhan-swift) |
| Kotlin | [`adhan-kotlin`](https://github.com/batoulapps/adhan-kotlin) |
| Java | [`adhan`](https://github.com/batoulapps/adhan-java) |
| Python | **`adhan-py`** (this library) |

## Features

- **Offline** — no network calls, no API keys
- **Timezone-aware** — returns UTC `datetime` objects, with optional `ZoneInfo` conversion
- **Multiple calculation methods** — Muslim World League, ISNA, Egyptian, Karachi, Umm al-Qura, Dubai, Moonsighting Committee, and more
- **Polar region support** — configurable strategies for locations above the Arctic/Antarctic circles
- **High latitude rules** — middle of the night, seventh of the night, twilight angle
- **Madhab selection** — Shafi (default) and Hanafi for Asr calculation
- **Qibla direction** — degrees clockwise from north
- **Sunnah times** — middle and last third of the night
- **CLI** — `python -m adhan` for quick terminal output
- **Fully typed** — PEP 561 `py.typed` marker, `mypy --disallow-untyped-defs` clean

## Requirements

- Python >= 3.11

## Installation

```bash
pip install adhan-py
```

## Quick Start

```python
from datetime import datetime
from adhan import PrayerTimes, CalculationMethod, Prayer

# Coordinates for Raleigh, NC
coordinates = (35.7750, -78.6336)
today = datetime.now()

prayer_times = PrayerTimes(
    coordinates,
    today,
    CalculationMethod.NORTH_AMERICA,
)

print(f"Fajr:    {prayer_times.fajr.strftime('%H:%M')}")
print(f"Sunrise: {prayer_times.sunrise.strftime('%H:%M')}")
print(f"Dhuhr:   {prayer_times.dhuhr.strftime('%H:%M')}")
print(f"Asr:     {prayer_times.asr.strftime('%H:%M')}")
print(f"Maghrib: {prayer_times.maghrib.strftime('%H:%M')}")
print(f"Isha:    {prayer_times.isha.strftime('%H:%M')}")
```

## Usage

### Timezone Conversion

Pass a `ZoneInfo` object to get times in that timezone:

```python
from zoneinfo import ZoneInfo
from adhan import PrayerTimes, CalculationMethod

london_zone = ZoneInfo("Europe/London")
prayer_times = PrayerTimes(
    (51.5074, -0.1278),
    datetime.now(),
    CalculationMethod.MOON_SIGHTING_COMMITTEE,
    time_zone=london_zone,
)
```

### Custom Calculation Parameters

```python
from adhan import PrayerTimes, CalculationParameters

params = CalculationParameters(
    fajr_angle=18,
    isha_angle=18,
    isha_interval=90,  # Isha = Maghrib + 90 minutes
)
prayer_times = PrayerTimes(
    coordinates,
    today,
    calculation_parameters=params,
)
```

### Qibla Direction

```python
from adhan import Qibla

direction = Qibla((35.7750, -78.6336)).direction
print(f"Qibla: {direction:.1f}° clockwise from north")
```

### Sunnah Times

```python
from adhan import PrayerTimes, SunnahTimes, CalculationMethod

prayer_times = PrayerTimes(coordinates, today, CalculationMethod.MUSLIM_WORLD_LEAGUE)
sunnah = SunnahTimes(prayer_times)

print(f"Middle of the night: {sunnah.middle_of_the_night}")
print(f"Last third:         {sunnah.last_third_of_the_night}")
```

### Polar Regions

```python
from adhan import PrayerTimes, CalculationParameters, PolarCircleRule

params = CalculationParameters(
    polar_circle_rule=PolarCircleRule.NEAREST_LATITUDE,  # default
)
prayer_times = Prayer_times(
    (78.2232, 15.6267),  # Longyearbyen, Svalbard
    datetime.now(),
    calculation_parameters=params,
)
```

### Command Line

```bash
python -m adhan --latitude 35.7750 --longitude -78.6336 --date 2015-07-12 --method NORTH_AMERICA
```

Output:
```
fajr=2015-07-12T08:42:00+00:00
sunrise=2015-07-12T10:08:00+00:00
dhuhr=2015-07-12T17:21:00+00:00
asr=2015-07-12T21:09:00+00:00
maghrib=2015-07-13T00:32:00+00:00
isha=2015-07-13T01:57:00+00:00
```

## API Reference

See [`docs/api.md`](docs/api.md) for the full API reference.

## Examples

See [`src/example/`](src/example/) for comprehensive examples covering:
- Basic usage
- Calculation methods comparison
- Qibla direction
- Sunnah times
- Polar region strategies
- High latitude rules
- Madhab selection
- CLI usage

## Development

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup and contribution guidelines.

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for a high-level overview of the codebase.

## Attribution & References

### Original Authors & Projects

- **batoulapps** — Original `adhan` library in [Java](https://github.com/batoulapps/adhan-java), [JavaScript](https://github.com/batoulapps/adhan-js), [Swift](https://github.com/batoulapps/adhan-swift), and [Kotlin](https://github.com/batoulapps/adhan-kotlin). The astronomical calculation methods, formulas, and overall architecture are derived from these implementations.
- **alphahm** — Original [adhanpy](https://github.com/alphahm/adhanpy) Python port. This fork continues from that work.

### Astronomical Calculation Sources

The prayer time calculation methods, mathematical formulas, and computational steps are derived from:

- **Jean Meeus** — *Astronomical Algorithms* (2nd ed., Willmann-Bell, 1998). The core astronomical formulas for solar position, equation of time, and hour angle calculations.
- **US Naval Observatory (USNO)** — Solar position algorithms and twilight calculations. Reference: [aa.usno.navy.mil](https://aa.usno.navy.mil/)
- **PrayTimes.org** — Standard prayer time calculation methods and Fajr/Isha angle conventions. Reference: [praytimes.org](https://praytimes.org/)
- **Muslim World League** — Fajr angle 18°, Isha angle 17°
- **ISNA (Islamic Society of North America)** — Fajr angle 15°, Isha angle 15°
- **Egyptian General Authority of Survey** — Fajr angle 19.5°, Isha angle 17.5°
- **University of Islamic Sciences, Karachi** — Fajr angle 18°, Isha angle 18°
- **Umm al-Qura University, Makkah** — Fajr angle 18.5°, Isha interval 90 minutes
- **Moonsighting Committee** — Fajr angle 18°, Isha angle 18°, with seasonal adjustments

### License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Credits

- **batoulapps** — original `adhan` implementation and calculation methods
- **alphahm** — original `adhanpy` Python port
- **Azahari Zaman** — community maintenance of `adhan-py`
