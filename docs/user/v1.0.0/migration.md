---
title: Migration
description: Migrate from adhanpy to al-falak.
slug: v1.0.0/migration
---

# Migration

This guide covers migrating from the original `adhanpy` package to `al-falak`.

## Package rename

```bash
# Old
pip install adhanpy

# New
pip install al-falak
```

## Import changes

```python
# Old
from adhanpy import PrayerTimes, CalculationMethod

# New
from alfalak import PrayerTimes, CalculationMethod
```

## Module structure

The internal module structure has changed:

```python
# Old
from adhanpy.calculation import CalculationMethod
from adhanpy.data import Coordinates

# New
from alfalak.calculation import CalculationMethod
from alfalak.data import Coordinates
```

## Error handling

The error hierarchy has been introduced in v1.0.0:

```python
# Old (adhanpy 1.x)
try:
    PrayerTimes(...)
except RuntimeError:
    ...

# New (al-falak 1.x)
from alfalak import AlFalakError, AstronomicalError

try:
    PrayerTimes(...)
except AstronomicalError:
    ...
```

## Breaking changes in v1.0.0

| Change | Old behavior | New behavior |
|---|---|---|
| Error types | `RuntimeError`, `ValueError`, `TypeError` | `AlFalakError` subclasses |
| Package name | `adhanpy` | `al-falak` |
| Import name | `import adhanpy` | `import alfalak` |
| Python support | 3.9+ | 3.11+ |

## Unchanged

* Calculation math (same formulas, same results)
* Public API surface (same class and method names)
* CLI interface (same arguments, same output format)

## See also

* [Changelog](/v1.0.0/changelog/) — full version history
* [API Reference](/v1.0.0/api-reference/) — current API
