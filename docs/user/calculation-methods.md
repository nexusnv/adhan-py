---
title: Calculation Methods
description: Compare all supported prayer time calculation methods.
---

# Calculation Methods

adhan-py supports 11 calculation methods. Each method defines Fajr and Isha angles (or intervals) and may include additional adjustments.

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

## Using a method

```python
from adhan import PrayerTimes, CalculationMethod

prayer_times = PrayerTimes(
    coordinates,
    datetime.now(),
    CalculationMethod.MUSLIM_WORLD_LEAGUE,
)
```

## Custom parameters

Override any method's defaults with `CalculationParameters`:

```python
from adhan import CalculationParameters

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
