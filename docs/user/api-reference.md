---
title: API Reference
description: Complete API reference for adhan-py.
---

# API Reference

All public names are importable from the package root:

```python
from adhan import (
    PrayerTimes,
    Qibla,
    SunnahTimes,
    CalculationMethod,
    CalculationParameters,
    HighLatitudeRule,
    Madhab,
    PolarCircleRule,
    PrayerAdjustments,
    Coordinates,
    Prayer,
    AdhanError,
    AstronomicalError,
    ConfigurationError,
    ValidationError,
)
```

## PrayerTimes

```python
PrayerTimes(
    coordinates: tuple[float, float] | Coordinates,
    date: datetime | DateComponents,
    calculation_method: CalculationMethod | None = None,
    calculation_parameters: CalculationParameters | None = None,
    time_zone: ZoneInfo | None = None,
)
```

Exactly one of `calculation_method` or `calculation_parameters` must be provided.

**Attributes:**

| Attribute | Type | Description |
|---|---|---|
| `fajr` | `datetime` | Fajr time |
| `sunrise` | `datetime` | Sunrise time |
| `dhuhr` | `datetime` | Dhuhr time |
| `asr` | `datetime` | Asr time |
| `maghrib` | `datetime` | Maghrib time |
| `isha` | `datetime` | Isha time |
| `coordinates` | `Coordinates` | Location coordinates |
| `calculation_parameters` | `CalculationParameters` | Parameters used |
| `time_zone` | `ZoneInfo \| None` | Timezone (if set) |

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `time_for_prayer(prayer: Prayer)` | `datetime` | Get time for a specific prayer |

## Qibla

```python
Qibla(coordinates: tuple[float, float] | Coordinates)
```

**Attributes:**

| Attribute | Type | Description |
|---|---|---|
| `direction` | `float` | Degrees clockwise from north |

## SunnahTimes

```python
SunnahTimes(prayer_times: PrayerTimes)
```

**Attributes:**

| Attribute | Type | Description |
|---|---|---|
| `middle_of_the_night` | `datetime` | Midpoint between Maghrib and Fajr |
| `last_third_of_the_night` | `datetime` | Start of last third of the night |

## CalculationParameters

```python
CalculationParameters(
    method: CalculationMethod | None = None,
    adjustments: PrayerAdjustments | None = None,
    method_adjustments: PrayerAdjustments | None = None,
    isha_interval: int = 0,
    fajr_angle: float = 0.0,
    isha_angle: float = 0.0,
    polar_circle_rule: PolarCircleRule = PolarCircleRule.NEAREST_LATITUDE,
)
```

**Attributes (settable):**

| Attribute | Type | Default | Description |
|---|---|---|---|
| `madhab` | `Madhab` | `Madhab.SHAFI` | Asr calculation method |
| `high_latitude_rule` | `HighLatitudeRule` | `MIDDLE_OF_THE_NIGHT` | High latitude rule |
| `polar_circle_rule` | `PolarCircleRule` | `NEAREST_LATITUDE` | Polar region strategy |
| `fajr_angle` | `float` | From method | Fajr angle in degrees |
| `isha_angle` | `float` | From method | Isha angle in degrees |
| `isha_interval` | `int` | From method | Isha interval in minutes |
| `method` | `CalculationMethod` | `NONE` | Calculation method |
| `adjustments` | `PrayerAdjustments` | — | Per-prayer minute offsets |
| `method_adjustments` | `PrayerAdjustments` | — | Method-specific offsets |

## Enums

### CalculationMethod

`NONE`, `MUSLIM_WORLD_LEAGUE`, `EGYPTIAN`, `KARACHI`, `UMM_AL_QURA`, `DUBAI`, `MOON_SIGHTING_COMMITTEE`, `NORTH_AMERICA`, `KUWAIT`, `QATAR`, `SINGAPORE`, `UOIF`

### HighLatitudeRule

`MIDDLE_OF_THE_NIGHT`, `SEVENTH_OF_THE_NIGHT`, `TWILIGHT_ANGLE`

### Madhab

`SHAFI`, `HANAFI`

### PolarCircleRule

`NONE`, `NEAREST_LATITUDE`, `NEAREST_DAY`, `MAKKAH`

### Prayer

`NONE`, `FAJR`, `SUNRISE`, `DHUHR`, `ASR`, `MAGHRIB`, `ISHA`

## Data types

### Coordinates

```python
Coordinates(latitude: float, longitude: float)
```

Validates that latitude is in [-90, 90] and longitude is in [-180, 180].

### PrayerAdjustments

```python
PrayerAdjustments(
    fajr: int = 0,
    sunrise: int = 0,
    dhuhr: int = 0,
    asr: int = 0,
    maghrib: int = 0,
    isha: int = 0,
)
```

## Exceptions

```
AdhanError (base)
├── AstronomicalError
├── ConfigurationError
└── ValidationError
```

## See also

- [Getting Started](/getting-started/) — quick start guide
- [Calculation Methods](/calculation-methods/) — method details
- [Errors](/errors/) — error handling
