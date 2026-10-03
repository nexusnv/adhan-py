# Changelog

## 1.1.0 — 2026-10-03 (phases 1–3: geodesy, twilight markers, night divisions)

> Scope: this release lands milestone phases 1–3 only (core geodesy,
> solar/twilight markers, night divisions). Phase 4 (Hijri/moon-sighting:
> lunar ephemeris, Yallop/Odeh, MABIMS) and phase 5+ remain for the next
> minor release. No breaking API changes from 1.0.0.

* Phase 1 — geodesy and calendrical hardening:
  * Lock JD/J2000 goldens (Meeus Ch.7) and document the Gregorian-only
    limitation (no Julian-calendar branch; correct for prayer use).
  * Lock Qibla spherical bearing goldens; move `MAKKAH` into canonical
    `data/Constants.py` (4-dp canonical `21.4225N, 39.8262E`, 7-dp digits
    kept for cross-port compat); document spherical-vs-ellipsoidal error
    (typically few arcmin, worst ~0.3–0.35°) and degenerate
    Makkah-to-self/antipode behavior (float in [0,360), no raise).
  * Add `Qibla.distance_to_makkah_km` (haversine `atan2` form,
    `R = 6371.0088 km` IUGG mean radius pinned).
  * Add opt-in `Qibla(method="ellipsoidal")` Karney inverse on WGS84
    (`astronomy/Geodesy.py`); spherical stays default; unknown method
    raises `ConfigurationError`.
  * Add `Qibla.magnetic_direction(declination_deg)` pure hook
    (`true − declination_east`, NOAA east-positive; model lookup stays
    caller-side; future WMM/IGRF provider must take `(model, epoch)`).
  * Document geodesy accuracy budget, Kaaba precision, and why Haversine
    alone is not high-precision (`docs/user/qibla.md`).
* Phase 2 — twilight and prayer markers:
  * Lock one golden day per twilight preset (all 11 + `NONE`); pin
    `MWL 18/17`, `EGYPTIAN 19.5/17.5`, `NORTH_AMERICA 15/15 (ISNA)`,
    `SINGAPORE 20/18 (MUIS)`; record Dubai-offset provenance and the
    Qatar 18-vs-18.5 source conflict as doc notes.
  * Add `CalculationMethod.JAKIM` (20/18, identical angles to `SINGAPORE`
    by design; Malay naming + zone metadata; verified against Takwim
    Malaysia Kuala Lumpur/Kota Kinabalu).
  * Add `imsak` marker (`Fajr − imsak_offset`, default 10 min,
    configurable); new `Prayer.IMSAK`, `PrayerAdjustments.imsak`,
    `time_for_prayer` support, CLI row.
  * Add `syuruk`/`ishraq`/`dhuha` markers derived from sunrise
    (`syuruk == sunrise`; `ishraq` default +15 min; `dhuha` window-start
    default +28 min, single Malaysian source; `dhuha_offset >=
    ishraq_offset` validated); new `Prayer` members, no `syuruk`
    adjustment slot by design (sunrise flows through).
  * Expose `equation_of_time(jd)` / `solar_declination(jd)` thin wrappers
    (Meeus Ch.28/Ch.25; transit path unchanged).
  * Add `elevation_m` observer correction (dip `0.0293°·√h_m`, metres;
    sunrise/sunset/Maghrib only; default 0 = unchanged goldens).
  * Add Umm al-Qura Ramadan mode (`is_ramadan: bool`, `UMM_AL_QURA`
    only; 120 min total vs 90 otherwise, not additive +30).
  * Document angle-vs-interval Isha, DUBAI/MSC offsets, seasonal
    twilight, and `HighLatitudeRule`/`PolarCircleRule` interaction.
* Phase 3 — night divisions:
  * Add `first_third_of_the_night` (Maghrib + ⅓ night).
  * Add generic `night_fraction(f, start=None, end=None)`
    (`0 < f < 1`, `int`/`float`/`Fraction`/`Decimal`; explicit aware
    anchors for Isha-anchored/sunset-anchored schools; UTC math,
    minute-rounded, `ValidationError` on bad fraction/interval).
  * Add `tahajjud_window` (`last_third → next-day Fajr`); existing
    `middle`/`last_third` become thin wrappers.
  * Night is Maghrib → next-day Fajr (offsets included); document rounding
    order and anchor alternatives (`docs/user/sunnah-times.md`).
* Docs: `docs/user/` topical pages cover every new marker/parameter
  (`calculation-methods`, `qibla`, `sunnah-times`, `api-reference`,
  `cli`, `citations`); `docs/user/v1.0.0/` frozen snapshot untouched.
* Tests: 653 collected; `black --check src/` → `ruff check src/ tests/`
  → `mypy src` → `pytest --cov-fail-under=95` green.

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
