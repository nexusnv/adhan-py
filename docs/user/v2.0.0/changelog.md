---
title: Changelog
description: Version history for adhan-py.
slug: v2.0.0/changelog
---

# Changelog

## 2.0.0

* **Breaking:** Package renamed from `adhanpy` to `adhan` (PyPI: `adhan-py`)
* **Breaking:** Dedicated `AdhanError` hierarchy replaces builtins (`AstronomicalError`, `ConfigurationError`, `ValidationError`)
* **Breaking:** Python >= 3.11 required (3.9/3.10 reached end-of-life)
* Fix hour-rollover in `rounded_minute` (`10:59:31` now rounds to `11:00`)
* Polar day/night and undefined Asr now raise with diagnostic messages
* Narrowed bare `except:` clauses
* Unknown madhab raises `ConfigurationError`; non-`CalculationMethod` method raises `TypeError`
* `PrayerTimes` accepts a `Coordinates` object as well as a tuple
* Method parameters are now copied per instance (no shared globals)
* Ship `py.typed` (PEP 561) and complete type annotations
* Define the public API surface (`__all__`-pinned)
* Add `PrayerTimes.time_for_prayer(Prayer)` accessor
* Add `Qibla` direction calculation
* Add polar-day/night estimation strategies (`PolarCircleRule`)
* Add `SunnahTimes` (middle and last third of the night)
* Add `python -m adhan` CLI
* Validate inputs: coordinates, angles, intervals
* Build backend is now hatchling (setup.py removed)
* Dev process: ruff lint gate, `mypy --disallow-untyped-defs`

## 1.0.5

* Fix `AttributeError` when method is not provided or set to `None`

## 1.0.4

* Fix rounding of minutes function incorrectly setting 60 for minutes
* Bring support for Python 3.9
