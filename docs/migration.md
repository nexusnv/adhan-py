# Migration notes (upstream `1.0.5` → this fork)

## Dropped interpreters

Python `>= 3.11` is required (`3.9`/`3.10` reached end-of-life).
CI covers `3.11`–`3.13`.

## Prayer-time values can shift by up to a minute

`rounded_minute` was fixed: hour carries (`10:59:31` → `11:00`,
was `10:59`), half-up rounding at exactly 30 seconds, and zeroed
microseconds. If you snapshot times, re-baseline.

## New error types for invalid input

- Non-`CalculationMethod` `method` → `TypeError` (was: silently `NONE`).
- Unknown `madhab` → `ValueError` (was: `AttributeError` / `None` leak).
- Polar day/night and undefined Asr → `RuntimeError` **with a
  diagnostic message** (was: empty `RuntimeError`).

Catch sites matching on the old silent behavior need updating.

## Wider accepted inputs (backward compatible)

- `PrayerTimes` coordinates: `(lat, lon)` tuple **or** `Coordinates`.
- `PrayerTimes` date: `datetime` **or** `DateComponents`.

## New capabilities

- `PrayerTimes.time_for_prayer(Prayer)` accessor.
- `Qibla(...).direction` (degrees clockwise from north).
- `SunnahTimes(prayer_times)` (`.middle_of_the_night`,
  `.last_third_of_the_night`).
- `python -m adhan` CLI (ISO-8601 UTC output).
- `py.typed`: downstream type-checkers now see annotations.
- Public imports from the `adhan` root (`__all__`-pinned).
- Per-instance `method_adjustments` (no longer shared globals).

## Unchanged

Calculation math itself is untouched apart from the rounding fix
above: same angles, methods, and twilight tables as upstream.

## 2.0.0 breaking change: AdhanError tree

Failures previously raised builtin `RuntimeError`/`ValueError`/
`TypeError` now raise `AdhanError` subclasses (`AstronomicalError`,
`ConfigurationError`, `ValidationError`) with identical messages.
Before: `except RuntimeError:` / After: `except adhan.AstronomicalError:`.
