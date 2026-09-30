---
title: Migration
description: Migrate from adhanpy to adhan-py.
---

# Migration

This guide covers migrating from the `adhanpy` package (`import adhanpy`,
[alphahm/adhanpy](https://github.com/alphahm/adhanpy)) to `adhan-py`
(`import adhan`, this library). The two are separate, independently released
libraries — not successive versions of the same package — but `adhan-py`
originates from the same [`batoulapps/adhan`](https://github.com/batoulapps/adhan)
port lineage, so the public surface keeps the same class and method names and
the switch is typically frictionless: change the install, change the import,
and handle the deliberate differences listed below.

## Why a separate library

`adhan-py` is maintained on its own so it can track currently supported Python
versions, keep development dependencies and tooling current, and let this
project's milestones evolve independently. In return you get a hardened,
fully typed codebase with explicit error handling (below) and ongoing
maintenance. Calculation math follows the same formulas, so prayer-time
values are comparable apart from the rounding fix noted in
[Changelog](/changelog/).

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

All public names are also importable from the package root (`from adhan import ...`).

## Error handling

The error hierarchy was introduced in v2.0.0:

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

Catch sites matching on the old behavior need updating: polar day/night and
undefined Asr raise `AstronomicalError`, bad method/madhab/polar-rule setup
raises `ConfigurationError`, and out-of-range coordinates/angles/intervals —
including non-numeric coordinates — raise `ValidationError`. See
[Errors](/errors/) for the full tree.

## Breaking changes in v2.0.0

| Change | Old behavior | New behavior |
|---|---|---|
| Error types | `RuntimeError`, `ValueError`, `TypeError` | `AdhanError` subclasses |
| Package name | `adhanpy` | `adhan-py` |
| Import name | `import adhanpy` | `import adhan` |
| Python support | 3.9+ | 3.11+ |

## Unchanged

- Calculation math (same formulas, same results; see the rounding fix in [Changelog](/changelog/))
- Public API surface (same class and method names)
- CLI interface (same arguments, same output format)

## See also

- [Changelog](/changelog/) — full version history
- [API Reference](/api-reference/) — current API
