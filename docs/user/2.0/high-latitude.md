---
title: High Latitude Rules
description: Handle prayer times at high latitudes with extreme night lengths.
slug: 2.0/high-latitude
---

# High Latitude Rules

At high latitudes, summer nights can be very short, making it difficult to determine Fajr and Isha times. adhan-py provides three rules for these situations.

## HighLatitudeRule options

| Rule | Behavior |
|---|---|
| `MIDDLE_OF_THE_NIGHT` | Fajr never earlier than middle of night, Isha never later (default) |
| `SEVENTH_OF_THE_NIGHT` | Fajr never earlier than start of last seventh, Isha never later than end of first seventh |
| `TWILIGHT_ANGLE` | Uses fajr\_angle/60 and isha\_angle/60 as night fractions |

## Using a high latitude rule

```python
from adhan import PrayerTimes, CalculationParameters, HighLatitudeRule

params = CalculationParameters(
    high_latitude_rule=HighLatitudeRule.MIDDLE_OF_THE_NIGHT,
)
prayer_times = PrayerTimes(
    (51.5074, -0.1278),  # London
    datetime.now(),
    calculation_parameters=params,
)
```

## MIDDLE\_OF\_THE\_NIGHT (default)

The night is split in half. Fajr cannot be earlier than the midpoint between sunset and sunrise, and Isha cannot be later than that midpoint.

## SEVENTH\_OF\_THE\_NIGHT

The night is split into sevenths. Fajr cannot be earlier than the start of the last seventh, and Isha cannot be later than the end of the first seventh.

## TWILIGHT\_ANGLE

Similar to seventh-of-the-night, but uses the Fajr and Isha angles divided by 60 as the night fraction. For example, with a Fajr angle of 18°, the fraction is 18/60 = 0.3 (30% of the night).

## When to use these rules

These rules are most relevant for locations above ~48° latitude during summer months:

| Latitude | Example locations |
|---|---|
| 48°–55° | Paris, Berlin, Kyiv, London |
| 55°–60° | Copenhagen, Oslo, Stockholm, St. Petersburg |
| 60°+ | Helsinki, Reykjavik, Anchorage, Longyearbyen |

## See also

* [Polar Regions](/2.0/polar-regions/) — handling polar day/night
* [Calculation Methods](/2.0/calculation-methods/) — method-specific defaults
