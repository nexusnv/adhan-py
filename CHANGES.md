# Changelog

## 1.0.0 — 2026-09-30 (first independent `al-falak` release)

> `al-falak` is versioned independently from `adhanpy` (a separate PyPI
> package). Entries below marked `1.0.5` / `1.0.4` are upstream `adhanpy`
> lineage, kept for provenance.

* Breaking: package renamed from `adhanpy` to `alfalak` (PyPI: `al-falak`).
* Breaking: dedicated `AlFalakError` hierarchy replaces builtins
  (`AstronomicalError`, `ConfigurationError`, `ValidationError`);
  messages unchanged. The internal isha-interval `ValueError` is untouched.
* Breaking: Python `>=3.11` required (3.9/3.10 reached end-of-life).
* Fix hour-rollover in `rounded_minute` (`10:59:31` now rounds to `11:00`),
  use half-up rounding at exactly 30 seconds, and zero microseconds.
* Polar day/night and undefined Asr now raise `AstronomicalError` with a
  diagnostic message instead of an empty `RuntimeError`.
* Narrowed bare `except:` clauses (`Astronomical.corrected_hour_angle`,
  `PrayerTimes._set_isha`).
* Unknown madhab raises `ConfigurationError`; non-`CalculationMethod` method raises
  `TypeError` (`None` still means `NONE`).
* `PrayerTimes` accepts a `Coordinates` object as well as a
  `(latitude, longitude)` tuple; fixed `src/example` header using the wrong date.
* Method parameters are now copied per instance: mutating one
  `CalculationParameters.method_adjustments` no longer leaks into
  subsequently created instances.
* Ship `py.typed` (PEP 561) and complete type annotations; the package
  is now `mypy --disallow-untyped-defs` clean with no runtime changes.
* Define the public API surface (`alfalak.__all__` plus `calculation`
  and `data` re-exports) and add `PrayerTimes.time_for_prayer(Prayer)`.
* Add `Qibla` direction calculation ported from upstream adhan.
* Add polar-day/night estimation strategies (`PolarCircleRule`:
  `NEAREST_LATITUDE` by default, `NEAREST_DAY`, `MAKKAH`, `NONE` to
  keep the old raise).
* Add `SunnahTimes` (middle and last third of the night) ported
  from upstream adhan.
* Add `python -m alfalak` CLI printing ISO-8601 UTC markers.
* Validate inputs: coordinates within [-90, 90]/[-180, 180], angles
  within [0, 90], non-negative Isha interval.
* Build backend is now hatchling (setup.py removed); CI covers
  Python 3.11–3.14.
* Asr is clamped to Dhuhr when polar-boundary geometry would place
  it earlier (total marker ordering now holds everywhere).
* Dev process: ruff lint gate (`F`, `E4/E7/E9`) over `src/` and
  `tests/`, and `mypy --disallow-untyped-defs` enforced via config.

## v1.0.5
* Fix [#16](https://github.com/alphahm/adhan/issues/16) where method is either not provided or
explicitly set to `None` when initialising `CalculationParameters` results in an `AttributeError`
in `PrayerTimes`

## v1.0.4
* Fix [#4](https://github.com/alphahm/adhan/issues/4) where rounding of minutes function tried to
incorrectly set 60 for minutes on a datetime object.
* Bring support for Python 3.9
