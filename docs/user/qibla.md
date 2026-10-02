---
title: Qibla Direction
description: Calculate the Qibla direction (degrees clockwise from north) for any location.
---

# Qibla Direction

The Qibla is the direction to the Kaaba in Makkah, used during Islamic prayer.

## Basic usage

```python
from alfalak import Qibla

direction = Qibla((35.7750, -78.6336)).direction
print(f"Qibla: {direction:.1f}° clockwise from north")
```

## Using a Coordinates object

```python
from alfalak import Qibla, Coordinates

coords = Coordinates(latitude=35.7750, longitude=-78.6336)
direction = Qibla(coords).direction
```

## Multiple cities

```python
from alfalak import Qibla

cities = [
    ("Raleigh, US", (35.7750, -78.6336)),
    ("London, UK", (51.5074, -0.1278)),
    ("Jakarta, ID", (-6.2088, 106.8456)),
    ("Sydney, AU", (-33.8688, 151.2093)),
]

for name, coords in cities:
    print(f"{name}: {Qibla(coords).direction:.1f}°")
```

## Distance to Makkah

```python
from alfalak import Qibla

qibla = Qibla((35.7750, -78.6336))
print(f"{qibla.direction:.1f}°, {qibla.distance_to_makkah_km:.0f} km")
```

## Ellipsoidal (WGS84) mode

The default above treats Earth as a sphere. For the precise geodesic on the
WGS84 ellipsoid (Karney inverse, stdlib-only, no new dependencies), opt in:

```python
from alfalak import Qibla

qibla = Qibla((35.7750, -78.6336), method="ellipsoidal")
print(f"{qibla.direction:.3f}°, {qibla.distance_to_makkah_km:.3f} km")
```

Any other `method` raises `ConfigurationError`. The spherical-vs-ellipsoidal
difference is typically a few arcminutes, worst case ~0.3–0.35° — use the
ellipsoidal mode when that matters to you, spherical otherwise.

## How it works (spherical default)

The default Qibla direction is calculated using spherical trigonometry:

```
direction = atan2(
    sin(Δlongitude),
    cos(latitude) × tan(Makkah_latitude) - sin(latitude) × cos(Δlongitude)
)
```

Where Makkah's coordinates are 21.4225°N, 39.8262°E.

This is a spherical-Earth model: typically within a few arcminutes of the
WGS84 ellipsoidal azimuth, worst case ~0.3–0.35° (per published
spherical-vs-ellipsoidal comparisons: IJRS great-circle study up to
~20 arcmin, Walisongo/Al-Hilal ~8 arcmin vs Vincenty). The 4-dp coordinate above
is canonical (~11 m); code carries extra display digits for compatibility.

Edge cases never raise: at Makkah itself the bearing is degenerate
(returns a float in [0, 360)), and at the true antipode
(~21.42°S, 140.17°W) every bearing is equidistant. Distance uses the
spherical great-circle with mean radius 6371.0088 km.

## See also

- [API Reference](/api-reference/) — full API documentation
- [Citations](/citations/) — attribution and references
