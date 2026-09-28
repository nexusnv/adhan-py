---
title: Migration
description: Migrate from adhanpy to adhan-py.
---

# Migration

This guide covers migrating from the original `adhanpy` package to `adhan-py`.

## Package rename

```bash
# Old
pip install adhanpy

# New
pip install adhan-py
```

## Import changes

```python
# Old
from adhanpy import PrayerTimes, CalculationMethod

# New
from adhan import PrayerTimes, CalculationMethod
```

## Module structure

The internal module structure has changed:

```python
# Old
from adhanpy.calculation import CalculationMethod
from adhanpy.data import Coordinates

# New
from adhan.calculation import CalculationMethod
from adhan.data import Coordinates
```

## Error handling

The error hierarchy has been introduced in v2.0.0:

```python
# Old (adhanpy 1.x)
try:
    PrayerTimes(...)
except RuntimeError:
    ...

# New (adhan-py 2.x)
from adhan import AdhanError, AstronomicalError

try:
    PrayerTimes(...)
except AstronomicalError:
    ...
```

## Breaking changes in v2.0.0

| Change | Old behavior | New behavior |
|---|---|---|
| Error types | `RuntimeError`, `ValueError`, `TypeError` | `AdhanError` subclasses |
| Package name | `adhanpy` | `adhan` |
| Import name | `import adhanpy` | `import adhan` |
| Python support | 3.9+ | 3.11+ |

## Unchanged

- Calculation math (same formulas, same results)
- Public API surface (same class and method names)
- CLI interface (same arguments, same output format)

## See also

- [Changelog](/changelog/) — full version history
- [API Reference](/api-reference/) — current API
