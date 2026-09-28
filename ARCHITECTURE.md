# Architecture

## Overview

`adhan-py` is an offline library for calculating Islamic prayer times. It follows a pipeline architecture: input coordinates and date flow through astronomical calculations to produce prayer time outputs.

## Package Structure

```
src/adhan/
├── __init__.py          # Public API re-exports
├── __main__.py          # CLI entry point (python -m adhan)
├── PrayerTimes.py       # Main prayer times calculator
├── Qibla.py             # Qibla direction calculator
├── SunnahTimes.py       # Sunnah night markers
├── exceptions.py        # AdhanError hierarchy
├── py.typed             # PEP 561 type marker
│
├── calculation/         # Calculation configuration
│   ├── CalculationMethod.py      # Enum of methods (MWL, ISNA, etc.)
│   ├── CalculationParameters.py # User-configurable parameters
│   ├── HighLatitudeRule.py       # Night portion rules
│   ├── Madhab.py                 # Shafi/Hanafi Asr
│   ├── PolarCircleRule.py        # Polar region strategies
│   ├── PrayerAdjustments.py      # Per-prayer minute offsets
│   ├── MethodsParameters.py      # Method-specific defaults
│   └── Twilight.py               # Seasonal twilight adjustments
│
├── astronomy/           # Astronomical calculations
│   ├── Astronomical.py           # Solar position algorithms
│   ├── CalendricalHelper.py      # Julian day/century conversions
│   ├── SolarCoordinates.py       # Sun's declination, right ascension
│   └── SolarTime.py              # Transit, sunrise, sunset, hour angles
│
├── data/                # Data types
│   ├── Coordinates.py            # Lat/lon with validation
│   ├── Prayer.py                 # Prayer enum (FAJR, SUNRISE, etc.)
│   ├── NightPortions.py          # Fajr/Isha night fractions
│   └── ShadowLength.py           # Asr shadow length factor
│
└── util/                # Utilities
    ├── CalendarUtil.py           # Minute rounding
    ├── DateComponents.py         # Date decomposition
    ├── FloatUtil.py              # Angle normalization
    └── TimeComponents.py         # Time decomposition
```

## Data Flow

```
Input: coordinates + date + calculation method/parameters
  │
  ▼
CalculationParameters ──► resolves method defaults, validates inputs
  │
  ▼
PolarCircleRule ──► resolves polar day/night (if needed)
  │
  ▼
SolarTime ──► computes transit, sunrise, sunset, hour angles
  │              (uses Astronomical + SolarCoordinates + CalendricalHelper)
  ▼
PrayerTimes ──► computes each prayer time:
  │              Fajr    = sunrise - night_portion (or twilight)
  │              Sunrise = solar sunrise
  │              Dhuhr   = solar transit
  │              Asr     = afternoon shadow length (madhab-dependent)
  │              Maghrib = solar sunset
  │              Isha    = sunset + night_portion (or interval)
  ▼
Output: timezone-aware UTC datetime for each prayer
```

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `PrayerTimes` | Orchestrates the calculation pipeline; public API |
| `Qibla` | Spherical trigonometry for direction to Makkah |
| `SunnahTimes` | Derives night markers from prayer times |
| `calculation/*` | Configuration, enums, method defaults |
| `astronomy/*` | Pure astronomical math (no prayer logic) |
| `data/*` | Immutable data types with validation |
| `util/*` | Shared helper functions |

## Error Hierarchy

```
AdhanError (base)
├── AstronomicalError    # Sun position undefined (polar day/night)
├── ConfigurationError   # Invalid setup (method, madhab, etc.)
└── ValidationError      # Out-of-range input (coordinates, angles)
```

## Design Principles

- **No external dependencies** — pure Python standard library
- **Fully typed** — all public APIs annotated, `py.typed` shipped
- **Immutable data** — `Coordinates`, `Prayer`, etc. are frozen dataclasses
- **Explicit errors** — no silent failures; all errors are `AdhanError` subclasses
- **Tested** — 100% line coverage, 99%+ branch coverage
