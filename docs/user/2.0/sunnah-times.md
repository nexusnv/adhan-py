---
title: Sunnah Times
description: Calculate Sunnah night markers — middle and last third of the night.
slug: 2.0/sunnah-times
---

# Sunnah Times

Sunnah times are recommended times for night prayer (Qiyam/Tahajjud), derived from the period between Maghrib and Fajr.

## Basic usage

```python
from datetime import datetime
from adhan import PrayerTimes, SunnahTimes, CalculationMethod

prayer_times = PrayerTimes(
    (35.7750, -78.6336),
    datetime.now(),
    CalculationMethod.MUSLIM_WORLD_LEAGUE,
)
sunnah = SunnahTimes(prayer_times)

print(f"Middle of the night: {sunnah.middle_of_the_night}")
print(f"Last third: {sunnah.last_third_of_the_night}")
```

## What are Sunnah times?

| Marker | Meaning |
|---|---|
| `middle_of_the_night` | Midpoint between Maghrib and Fajr |
| `last_third_of_the_night` | Start of the last third of the night (recommended for Qiyam) |

## With timezone

```python
from zoneinfo import ZoneInfo

tz = ZoneInfo("America/New_York")
prayer_times = PrayerTimes(
    coordinates,
    datetime.now(),
    CalculationMethod.MUSLIM_WORLD_LEAGUE,
    time_zone=tz,
)
sunnah = SunnahTimes(prayer_times)
```

## DST-safe

The calculation uses absolute elapsed time (UTC internally), so markers are correct even on nights with DST transitions.

## See also

* [API Reference](/2.0/api-reference/) — full API documentation
* [Timezone Handling](/2.0/timezone/) — timezone conversion details
