---
title: Qibla Direction
description: Calculate the Qibla direction (degrees clockwise from north) for any location.
slug: v1.0.0/qibla
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

## How it works

The Qibla direction is calculated using spherical trigonometry:

```
direction = atan2(
    sin(Δlongitude),
    cos(latitude) × tan(Makkah_latitude) - sin(latitude) × cos(Δlongitude)
)
```

Where Makkah's coordinates are 21.4225°N, 39.8262°E.

## See also

* [API Reference](/v1.0.0/api-reference/) — full API documentation
* [Citations](/v1.0.0/citations/) — attribution and references
