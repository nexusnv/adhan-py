# Black-box evidence report — pre-release feasibility sweep

## Scope

- Boundary: public Python API (`adhan` root exports: `PrayerTimes`, `Qibla`,
  `SunnahTimes`, `CalculationMethod`, `CalculationParameters`,
  `HighLatitudeRule`, `Madhab`, `PolarCircleRule`, `PrayerAdjustments`,
  `Coordinates`, `Prayer`, `AdhanError` hierarchy) + CLI consumer workflow
  (`adhan.__main__.main` in-process and `python -m adhan` subprocess).
  No private helpers, no internal state, no mocks, no call-order assertions.
  `DateComponents` (accepted public input type, no root export) used only as
  caller-side input construction, mirroring existing tests.
- Consumer: library consumer calling the public API with synthetic
  coordinates/dates; shell consumer running the installed `adhan` command.
- Target behavior and requested focus: pre-release feasibility sweep of prayer-time
  calculation across all methods/madhabs/rules, Qibla, SunnahTimes, CLI, and
  stable error types. No focus narrowing was requested; broad-by-default applied.
- Properties/invariants: P1 monotonic ordering
  `fajr < sunrise < dhuhr <= asr < maghrib < isha` (Dhuhr/Asr may coincide —
  documented saturation); P2 all outputs tz-aware (UTC by default); P3 all
  failures surface as `AdhanError` subclasses (per ARCHITECTURE.md); P4 Qibla
  direction in `[0, 360)`.
- Coverage areas/plan: 11 CalculationMethods (+NONE characterization), Shafi/Hanafi
  Asr shift, 3 HighLatitudeRules, 4 PolarCircleRules + no-op check, positive/negative/
  extreme PrayerAdjustments, Umm-al-Qura isha interval, UTC/ZoneInfo behavior,
  `time_for_prayer` dispatch, config/validation/astronomical errors, tuple vs
  Coordinates vs datetime vs DateComponents inputs, 7 Qibla goldens + poles/equator/
  antimeridian + Makkah-self, 3 SunnahTimes cases, 7 CLI cases.
  Exclusions (see Coverage gaps): locale matrix beyond NY/London, extreme years,
  performance, white-box internals.
- Broad coverage or focused coverage: broad
- Surfaces or cases outside the focus: none (broad sweep); see Coverage gaps for
  residual exclusions.
- Safety constraints: local-isolated synthetic execution only; no network, no
  secrets, no prod data; subprocess self-invocations use arg arrays (no shell),
  explicit timeouts, bounded capture; `src/` untouched (diagnosis-only run).

## Runner and environment

- Test runner and version: pytest 9.1.1 (via `uv run --with pytest --with pytest-cov`)
- Relevant dependency/tool versions: Python 3.14.6; adhan-py 2.0.0 (repo working
  tree, branch `chore/blackbox-param-feasibility-20260929`); tzdata from stdlib
  `zoneinfo`; no third-party runtime deps (pure stdlib).
- Working directory (project-relative or redacted): `.` (repo root)
- Environment fingerprint (OS/runtime and non-sensitive runtime details):
  Linux 6.12.107+deb13-amd64 x86_64, CPython 3.14.6
- Seed (or N/A with reason): N/A — no randomness; all inputs are fixed synthetic
  coordinates/dates.
- Environment mode: local-isolated
- Isolation/scope verification (exact method and result): code inspection of the
  sweep file — no socket/filesystem writes, no env reads; inputs are fixed
  synthetic tuples/dates; the only child processes are two `python -m adhan`
  self-invocations with literal arg arrays, `shell=False`, `timeout=60`,
  captured output. Result: isolated, verified 2026-09-29.
- run_approval_status: not-required
- run_approval_scope (target/method/data/volume/rate/time limits; budget when paid):
  local synthetic only; 66 scenarios, single-file pytest run, ~0.6 s; no rate/cost.
- credential_approval_status: not-required
- credential_approval_scope (target/service, least-privilege, synthetic/test-only, expiry/rotation, volume/rate/time limits): N/A — no authentication surface.
- Destructive scope (target/maximum affected resources/rollback/cleanup/permission; budget not applicable): none — no destructive action; no files/state created outside pytest capture and `test-reports/` markdown.
- Controlled environment, clock, locale, timezone, and identifiers: explicit calendar
  dates passed to every API call (no "now" dependence) except BB-CLI-02, which
  asserts only key presence; `ZoneInfo("America/New_York")` /
  `ZoneInfo("Europe/London")` pinned where wall-clock goldens apply; ambient locale
  (no locale-sensitive assertions).
- Optional tools unavailable: `pytest-mock` (`mocker` fixture) — 2 pre-existing
  tests in `tests/test_PrayerTimes.py` error at setup; not installed per
  no-new-framework constraint. See Coverage gaps.
- Report date: 2026-09-29

## Scenario matrix

`execution_id: pending` for all planning rows (actual IDs in Exact executions).
Common row values (repeated per row for schema completeness, abbreviated):
`environment_mode: local-isolated`; `isolation_scope_verification: arg-array
subprocess/timeout/code-inspection, verified`; `run_approval_status: not-required`;
`run_approval_scope: local synthetic, 66 scenarios, ~1 s, no budget`;
`credential_approval_status: not-required`; `credential_approval_scope: N/A — no auth`;
`Safety status: default-safe`; `Cleanup: N/A — no persistent state`;
`Expected side effects: none`.

| scenario_id | execution_id | Traceability | Label | Input class | Preconditions | Invocation | Properties/invariants | Coverage areas/plan | Expected result | Expected failure / not-applicable reason | Expected side effects | Cleanup | environment_mode | isolation_scope_verification | run_approval_status | run_approval_scope | credential_approval_status | credential_approval_scope | Safety status | planned_result_state |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BB-PT-METHOD-MWL | pending | multi-method support (README) | contract | valid | Raleigh 2015-07-12 UTC | `PrayerTimes(tuple, datetime, method)` | P1, P2 | MUSLIM_WORLD_LEAGUE ordering/UTC | ordered UTC times | not applicable | none | N/A | local-isolated | verified (see above) | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-EGYPTIAN | pending | same | contract | valid | same | same | P1, P2 | EGYPTIAN | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-KARACHI | pending | same | contract | valid | same | same | P1, P2 | KARACHI | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-UMM_AL_QURA | pending | same | contract | valid | same | same | P1, P2 | UMM_AL_QURA (interval-based Isha) | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-DUBAI | pending | same | contract | valid | same | same | P1, P2 | DUBAI (method adjustments) | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-MOON_SIGHTING | pending | same | contract | valid | same | same | P1, P2 | MOON_SIGHTING_COMMITTEE (seasonal) | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-NORTH_AMERICA | pending | same | contract | valid | same | same | P1, P2 | NORTH_AMERICA | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-KUWAIT | pending | same | contract | valid | same | same | P1, P2 | KUWAIT | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-QATAR | pending | same | contract | valid | same | same | P1, P2 | QATAR (interval-based Isha) | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-SINGAPORE | pending | same | contract | valid | same | same | P1, P2 | SINGAPORE | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-UOIF | pending | same | contract | valid | same | same | P1, P2 | UOIF | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-METHOD-NONE-01 | pending | no documented contract for NONE | characterization | boundary | Raleigh 2015-07-12 UTC | `PrayerTimes(tuple, datetime, NONE)` | P2 only | degenerate zero-angle method | tz-aware datetimes; ordering NOT guaranteed (observed fajr>sunrise, isha<maghrib) | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-GOLDEN-NA-01 | pending | tests/test_PrayerTimes.py `test_prayer_times_second_precision_locked` | contract | valid | Raleigh 2015-07-12, NORTH_AMERICA/HANAFI | `PrayerTimes` via params | exact UTC second precision | golden regression | 08:42/10:08/17:21/22:22/00:32/01:57 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-GOLDEN-MOON-01 | pending | tests/test_PrayerTimes.py `test_moon_sighting_method` | contract | valid | Raleigh 2016-01-31, MOON_SIGHTING_COMMITTEE | `PrayerTimes` via method | NY wall-clock golden | golden regression | 05:48 AM … 07:05 PM | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-MADHAB-01 | pending | README madhab; `Madhab.get_shadow_length` DOUBLE vs SINGLE | contract | valid | Raleigh 2015-07-12 MWL, Shafi vs Hanafi | `PrayerTimes` via params | Hanafi Asr later; others equal | madhab shift | hanafi.asr > shafi.asr; 5 others equal | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-HLR-MID | pending | documented high-latitude support | contract | boundary (high lat) | Oslo 2016-01-01 MWL | `PrayerTimes` via params | P1, P2 | MIDDLE_OF_THE_NIGHT | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-HLR-SEVENTH | pending | same | contract | boundary (high lat) | same | same | P1, P2 | SEVENTH_OF_THE_NIGHT | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-HLR-TWILIGHT | pending | same | contract | boundary (high lat) | same | same | P1, P2 | TWILIGHT_ANGLE | ordered UTC times | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-POLAR-01 | pending | tests/test_PrayerTimes.py `test_polar_night_error_message` | contract | boundary (polar night) | Tromso 2015-12-21, rule NONE | `PrayerTimes` via params | P3 stable error | polar refusal | not applicable | `AstronomicalError` matching `(?i)undefined\|polar` | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-POLAR-02 | pending | tests/test_PolarCircle.py `test_default_assumes_nearest_latitude` | contract | boundary (polar night) | Tromso 2015-12-21, default rule | `PrayerTimes` via params | P1 + clamp behavior | NEAREST_LATITUDE | ordered; 60 < lat < 69.65; lon kept | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-POLAR-03 | pending | tests/test_PolarCircle.py `test_nearest_day_keeps_location_but_shifts_date` | contract | boundary (polar night) | Tromso 2015-12-21, NEAREST_DAY | `PrayerTimes` via params | P1 + date shift | NEAREST_DAY | ordered; coords kept; fajr date != 2015-12-21 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-POLAR-04 | pending | tests/test_PolarCircle.py `test_makkah_rule_matches_makkah_schedule` | contract | boundary (polar night) | Tromso 2015-12-21, MAKKAH | `PrayerTimes` vs Makkah control | schedule equality | MAKKAH rule | coords == Makkah; all 6 times equal | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-POLAR-05 | pending | tests/test_PolarCircle.py `test_no_rule_change_on_normal_days` | contract | valid | Raleigh 2015-07-12, default vs NONE | `PrayerTimes` via params | no-op on normal days | rule neutrality | all 6 times equal | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-ADJ-01 | pending | tests/test_PrayerTimes.py `test_offsets` | contract | valid | Raleigh 2015-12-01 MWL, +10 each | `PrayerTimes` via params | exact +10.0 min shift | positive offsets | delta == 10.0 for all 6 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-ADJ-02 | pending | symmetric to BB-PT-ADJ-01 | contract | valid | same base, −15 fajr/isha | `PrayerTimes` via params | exact −15.0 min shift + P1 | negative offsets | deltas −15.0; still ordered | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-ADJ-03 | pending | tests/test_PolarCircle.py `test_extreme_adjustments_saturate_asr_to_dhuhr` | contract | boundary (extreme offset) | same base, dhuhr +180 | `PrayerTimes` via params | Asr clamp + P1 | saturation | asr == dhuhr; ordered | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-ISHA-01 | pending | tests/test_PrayerTimes.py `test_prayer_times_with_method_with_isha_interval` | contract | valid | Makkah 2022-08-08 UMM_AL_QURA | `PrayerTimes` via params | isha − maghrib == interval | interval contract | 90.0 min | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-TZ-01 | pending | README "Timezone-aware — returns UTC datetimes" | contract | valid | Raleigh 2015-07-12 MWL | `PrayerTimes` via method | P2 + zero offset | default UTC | all tz-aware; utcoffset 0 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-TZ-02 | pending | tests/test_PrayerTimes.py `test_prayer_times_timezone_conversion` | contract | valid | London 2022-01-01 + 2022-08-01 | `PrayerTimes` with `time_zone` | DST conversion goldens | ZoneInfo conversion | 06:25 AM / 02:37 AM / 03:37 AM | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-TIMEFOR-01 | pending | tests/test_public_api.py `test_time_for_prayer_matches_attributes` | contract | valid | Raleigh 2015-07-12 NORTH_AMERICA | `time_for_prayer(Prayer.*)` | dispatch equality | enum dispatch | 6 enum lookups match attrs | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-TIMEFOR-02 | pending | tests/test_public_api.py `test_time_for_prayer_rejects_none` | contract | invalid | same instance | `time_for_prayer(Prayer.NONE)` | P3 stable error | NONE rejection | not applicable | `ConfigurationError` matching `(?i)prayer` | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-CFG-01 | pending | tests/test_PrayerTimes.py `test_either_...` | contract | invalid | both method+params | `PrayerTimes` constructor | P3 stable error | exclusive-args | not applicable | `ConfigurationError` "Only one of" | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-CFG-02 | pending | same contract (neither branch) | contract | invalid | neither method nor params | `PrayerTimes` constructor | P3 stable error | exclusive-args | not applicable | `ConfigurationError` "Only one of" | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-CFG-03 | pending | tests/test_PrayerTimes.py `test_invalid_madhab_raises_configuration_error` | contract | invalid | madhab None | `PrayerTimes` via params | P3 stable error | bad madhab | not applicable | `ConfigurationError` | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-CFG-04 | pending | `night_portions()` else-branch | contract | invalid | high_latitude_rule "bogus" | `PrayerTimes` via params | P3 stable error | bad HLR | not applicable | `ConfigurationError` matching `(?i)high latitude` | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-CFG-05 | pending | tests/test_PolarCircle.py `test_unknown/invalid_polar_rule` | contract | invalid | polar rule "bogus" | `CalculationParameters` + `PrayerTimes` | P3 stable error | bad polar rule (both layers) | not applicable | `ConfigurationError` matching `(?i)polar` | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-VAL-01a | pending | tests/test_validation.py `test_out_of_range_tuple_rejected_by_prayer_times` | contract | invalid | lat 91 | `PrayerTimes` constructor | P3 stable error | coordinate range | not applicable | `ValidationError` matching latitude\|longitude | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-VAL-01b | pending | same | contract | invalid | lon 181 | `PrayerTimes` constructor | P3 stable error | coordinate range | not applicable | `ValidationError` matching latitude\|longitude | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-VAL-02a | pending | tests/test_validation.py `test_out_of_range_parameters_rejected` | contract | invalid | fajr_angle 91 | `CalculationParameters` | P3 stable error | angle range | not applicable | `ValidationError` matching angle\|interval | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-VAL-02b | pending | same | contract | invalid | isha_angle −1 | `CalculationParameters` | P3 stable error | angle range | not applicable | `ValidationError` matching angle\|interval | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-VAL-02c | pending | same | contract | invalid | isha_interval −5 | `CalculationParameters` | P3 stable error | interval range | not applicable | `ValidationError` matching angle\|interval | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-VAL-03 | pending | ARCHITECTURE.md "all errors are AdhanError subclasses" | suspicious current behavior | invalid | non-numeric `("a", "b")` | `PrayerTimes` constructor | P3 (predicts AdhanError) | input-type rejection | not applicable | `AdhanError` (any subclass) | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned open (leak suspected) |
| BB-PT-INPUT-01 | pending | tests/test_PrayerTimes.py `test_prayer_times_accepts_coordinates_object` | contract | valid | Raleigh tuple vs Coordinates | `PrayerTimes` both shapes | input equivalence | coordinates shapes | fajr/isha equal | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-PT-INPUT-02 | pending | tests/test_PrayerTimes.py `test_prayer_times_accepts_datetime_and_date_components` | contract | valid | 2015-07-12 datetime vs DateComponents | `PrayerTimes` both shapes | input equivalence | date shapes | fajr/isha equal | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-01 | pending | tests/test_Qibla.py (Raleigh 55.825) | contract | valid | Raleigh | `Qibla(tuple)` + `Qibla(Coordinates)` | approx ±0.01 + P4 | bearings | 55.825 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-02 | pending | same (New York 58.482) | contract | valid | New York | same | same | bearings | 58.482 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-03 | pending | same (London 118.987) | contract | valid | London | same | same | bearings | 118.987 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-04 | pending | same (Cairo 136.137) | contract | valid | Cairo | same | same | bearings | 136.137 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-05 | pending | same (Kuala Lumpur 292.538) | contract | valid | Kuala Lumpur | same | same | bearings | 292.538 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-06 | pending | same (Jakarta 295.152) | contract | valid | Jakarta | same | same | bearings | 295.152 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-07 | pending | same (Sydney 277.500) | contract | valid | Sydney | same | same | bearings | 277.500 | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-SELF-01 | pending | degenerate atan2(0, ~0) — no documented contract | characterization | boundary | Makkah self | `Qibla(makkah)` | returns float in range | self-bearing | 180.0 observed ±1e-6, in [0,360) | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-EDGE-01 | pending | P4 range matcher | contract | boundary | (0, 0) | `Qibla(tuple)` | P4 | cardinal | in [0, 360) | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-EDGE-02 | pending | P4 range matcher | contract | boundary | (90, 0) north pole | `Qibla(tuple)` | P4 | cardinal | in [0, 360) | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-EDGE-03 | pending | P4 range matcher | contract | boundary | (−90, 0) south pole | `Qibla(tuple)` | P4 | cardinal | in [0, 360) | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-QIBLA-EDGE-04 | pending | P4 range matcher | contract | boundary | (0, 180) antimeridian | `Qibla(tuple)` | P4 | cardinal | in [0, 360) | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-SUNNAH-01 | pending | tests/test_SunnahTimes.py `test_sunnah_times` | contract | valid | Raleigh MWL 2015-07-12 | `SunnahTimes(prayer_times)` | exact UTC goldens | night markers | 04:28 / 05:46 on 2015-07-13 UTC | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-SUNNAH-02 | pending | tests/test_SunnahTimes.py `test_sunnah_times_ordering` | contract | valid | same + next-day control (public datetime) | `SunnahTimes` + control `PrayerTimes` | night ordering | marker ordering | maghrib < middle < last-third < tomorrow fajr | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-SUNNAH-03 | pending | tests/test_SunnahTimes.py `test_sunnah_times_across_dst_transition` | contract | boundary (DST) | Raleigh 2015-03-07 America/New_York | `SunnahTimes` tz-aware | DST-absolute goldens | DST transition | 23:43 / 01:32 in NY tz | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-01 | pending | tests/test_cli.py `test_cli_prints_iso_times` | contract | valid | args lat/lon/date/NORTH_AMERICA | `main(argv)` in-process | exact fajr + ISO parse | happy path | 6 keys; fajr 2015-07-12T08:42:00+00:00; all parse aware | not applicable | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-02 | pending | tests/test_cli.py `test_cli_module_entry_point` | contract | valid | args lat/lon only | `python -m adhan` subprocess | exit 0 + key presence | module entry | returncode 0; `fajr=` in stdout | not applicable | none | N/A | local-isolated | verified (arg array, timeout 60) | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-03 | pending | argparse usage contract | contract | invalid | `--method BOGUS` | `main(argv)` in-process | exit status 2 | unknown method | not applicable | SystemExit code 2 | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-04 | pending | tests/test_cli.py `test_cli_rejects_bad_date` | contract | invalid | `--date not-a-date` | `main(argv)` in-process | exit status 2 | bad date | not applicable | SystemExit code 2 | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-05 | pending | tests/test_cli.py `test_cli_rejects_datetime_for_date` | contract | invalid | `--date 2015-07-12T00:00:00` | `main(argv)` in-process | exit status 2 | datetime date | not applicable | SystemExit code 2 | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-06 | pending | tests/test_cli.py `test_cli_requires_coordinates` | contract | invalid | `--latitude 35` only | `main(argv)` in-process | exit status 2 | missing coords | not applicable | SystemExit code 2 | none | N/A | local-isolated | verified | not-required | local synthetic | not-required | N/A | default-safe | planned |
| BB-CLI-07 | pending | no documented exit mapping for domain errors | characterization | invalid | `--latitude 91` | `python -m adhan` subprocess | nonzero exit + type on stderr | domain error via CLI | returncode != 0; `ValidationError` in stderr (exact code/message NOT pinned) | not applicable | none | N/A | local-isolated | verified (arg array, timeout 60) | not-required | local synthetic | not-required | N/A | default-safe | planned |

## Oracles and normalization

| Scenario | Named oracle | Observable boundary | Authority or evidence source | Normalization |
| --- | --- | --- | --- | --- |
| BB-PT-METHOD-* (11) | monotonic invariant P1 + UTC-aware P2 | return values of `PrayerTimes` attributes | documented multi-method support + UTC guarantee (README, ARCHITECTURE.md) | none |
| BB-PT-METHOD-NONE-01 | characterization (observed inversion) | same | none — open behavior, recorded 2026-09-29 | none |
| BB-PT-GOLDEN-NA-01 | reviewed golden, second precision | `fajr…isha` UTC strings | tests/test_PrayerTimes.py `test_prayer_times_second_precision_locked` | none |
| BB-PT-GOLDEN-MOON-01 | reviewed golden, NY wall clock | attributes via `astimezone` | tests/test_PrayerTimes.py `test_moon_sighting_method` | none |
| BB-PT-MADHAB-01 | exact relational outcome (Hanafi later, rest equal) | `asr` + 5 attributes | README madhab docs; `Madhab.get_shadow_length` | none |
| BB-PT-HLR-* (3) | invariant P1 + P2 | attributes | documented high-latitude support | none |
| BB-PT-POLAR-01 | stable error (`AstronomicalError`, fragment) | raised exception type/message | tests/test_PrayerTimes.py `test_polar_night_error_message` | message matched by regex fragment only |
| BB-PT-POLAR-02..05 | invariant P1 + rule-specific equality | attributes + `coordinates` | tests/test_PolarCircle.py | none |
| BB-PT-ADJ-01/02 | exact minute-shift arithmetic | attribute deltas | tests/test_PrayerTimes.py `test_offsets` (01); symmetry (02) | none |
| BB-PT-ADJ-03 | saturation equality + P1 | `asr`, `dhuhr` | tests/test_PolarCircle.py `test_extreme_adjustments_saturate_asr_to_dhuhr` | none |
| BB-PT-ISHA-01 | exact duration (90 min) | `isha − maghrib` | tests/test_PrayerTimes.py `test_prayer_times_with_method_with_isha_interval` | none |
| BB-PT-TZ-01 | contract matcher (tz-aware, zero offset) | `tzinfo`/`utcoffset` | README timezone guarantee | none |
| BB-PT-TZ-02 | conversion goldens (incl. DST) | attributes in zone | tests/test_PrayerTimes.py `test_prayer_times_timezone_conversion` | none |
| BB-PT-TIMEFOR-01/02 | dispatch equality / stable error | return values / raised type | tests/test_public_api.py | none |
| BB-PT-CFG-01..05 | stable error type + fragment | raised type/message | tests/test_PrayerTimes.py, tests/test_PolarCircle.py | message matched by fragment only |
| BB-PT-VAL-01/02 | stable error type + fragment | raised type/message | tests/test_validation.py | message matched by fragment only |
| BB-PT-VAL-03 | stable-error expectation (P3: any `AdhanError`) | raised type | ARCHITECTURE.md error-tree contract | none — FAILED, see Failures |
| BB-PT-INPUT-01/02 | input-shape equivalence | attribute equality | tests/test_PrayerTimes.py | none |
| BB-QIBLA-01..07 | reviewed goldens ±0.01° | `.direction` | tests/test_Qibla.py (published bearings/WGS84 cross-check per comment) | tolerance ±1e-2 (documented precision, not volatility) |
| BB-QIBLA-SELF-01 | characterization (observed 180.0) | `.direction` | none — degenerate case, recorded 2026-09-29 | tolerance ±1e-6 on recorded value |
| BB-QIBLA-EDGE-01..04 | range matcher P4 | `.direction` | spherical-trig contract (degrees in [0,360)) | none |
| BB-SUNNAH-01/03 | reviewed goldens | night-marker datetimes | tests/test_SunnahTimes.py | none |
| BB-SUNNAH-02 | ordering invariant | marker vs maghrib/tomorrow-fajr | tests/test_SunnahTimes.py | none |
| BB-CLI-01 | exact stdout golden + ISO parse | captured stdout | tests/test_cli.py `test_cli_prints_iso_times` | none |
| BB-CLI-02 | exit status + key presence | returncode/stdout | tests/test_cli.py `test_cli_module_entry_point` | date defaults to today — value not pinned, only `fajr=` presence |
| BB-CLI-03..06 | argparse exit status 2 | SystemExit code | argparse usage contract; tests/test_cli.py | none |
| BB-CLI-07 | characterization (nonzero exit + type name) | returncode/stderr | none — unspecified mapping, recorded 2026-09-29 | exact code/message NOT pinned (deliberately) |

No normalization of volatile fields was needed: every API call uses explicit fixed
dates (no clock dependence), no randomness, no temp paths. The single
today-dependent case (BB-CLI-02) pins only key presence, never values.

## Exact executions

| execution_id | scenario_ids | Environment mode | Isolation/scope verification | run_approval_status | run_approval_scope | credential_approval_status | credential_approval_scope | Working directory (project-relative or redacted) | Command (redacted; structure preserved) | Command replay note | Exit status | Runner | Environment fingerprint | Relevant bounded excerpt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution-001 | all 66 BB-* | local-isolated | code inspection: no net/fs/env; arg-array subprocess, timeout 60 | not-required | local synthetic, ~1 s, no budget | not-required | N/A — no auth | `.` | `uv run --with pytest --with pytest-cov -- pytest tests/test_blackbox_sweep_tmp.py -p no:cacheprovider -q` | exact replayable command; no redaction needed (no secrets/paths) | 1 | pytest 9.1.1 / CPython 3.14.6 | Linux 6.12.107+deb13-amd64 x86_64 | `2 failed, 64 passed` (1 test-file NameError + 1 product TypeError) |
| execution-002 | all 66 BB-* | local-isolated | same as execution-001 | not-required | local synthetic, ~1 s, no budget | not-required | N/A — no auth | `.` | `uv run --with pytest --with pytest-cov -- pytest tests/test_blackbox_sweep_tmp.py -p no:cacheprovider -q` | rerun after fixing missing `AstronomicalError` import in sweep file | 1 | pytest 9.1.1 / CPython 3.14.6 | Linux 6.12.107+deb13-amd64 x86_64 | `1 failed, 65 passed in 0.57s` |
| execution-003 | BB-PT-VAL-03 (+variants) | local-isolated | code inspection: read-only probes, synthetic inputs, bounded prints | not-required | local synthetic, <1 s | not-required | N/A — no auth | `.` | `uv run --with pytest -- python -c "<synthetic coordinate variants probe>"` | inline probe (full text in Failures reproducer); no redaction needed | 0 | CPython 3.14.6 | Linux 6.12.107+deb13-amd64 x86_64 | 5 LEAK variants (`TypeError`/`ValueError`); NaN/inf correctly `ValidationError`; `Qibla` leaks `TypeError` too |
| execution-004 | all BB-* (sanity: full repo suite) | local-isolated | same as execution-001 | not-required | local synthetic, ~2 s | not-required | N/A — no auth | `.` | `uv run --with pytest --with pytest-cov -- pytest -p no:cacheprovider -q` | full-suite sanity incl. parallel agent file and pre-existing tests | 1 | pytest 9.1.1 / CPython 3.14.6 | Linux 6.12.107+deb13-amd64 x86_64 | `8 failed, 454 passed, 2 errors in 1.47s` (1 mine + 7 parallel-agent file + 2 pre-existing `mocker` errors) |

## Results

All rows linked to execution-002 (definitive sweep run), except BB-PT-VAL-03 which
is additionally linked to execution-003 (minimization). `retry_of_execution_id`
is `N/A` throughout (no retries; execution-002 is a rerun after a test-file fix,
not a retry of a flaky result — the product outcome was stable across both runs).

| execution_id | scenario_id | result_state | observed_public_outcome | evidence_reference | retry_of_execution_id | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| execution-002 | BB-PT-METHOD-MWL | pass | ordered UTC times (fajr 08:22 … isha 02:11) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-EGYPTIAN | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-KARACHI | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-UMM_AL_QURA | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-DUBAI | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-MOON_SIGHTING | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-NORTH_AMERICA | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-KUWAIT | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-QATAR | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-SINGAPORE | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-UOIF | pass | ordered UTC times | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-METHOD-NONE-01 | pass | tz-aware; fajr 10:13 > sunrise 10:08; isha 00:28 < maghrib 00:32 (characterization holds) | execution-002 excerpt | N/A | corroborated by parallel sweep's NONE ordering failures (read-only observation) |
| execution-002 | BB-PT-GOLDEN-NA-01 | pass | exact second-precision golden match | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-GOLDEN-MOON-01 | pass | NY wall-clock golden match | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-MADHAB-01 | pass | Hanafi asr 22:22 > Shafi 21:09; other 5 equal | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-HLR-MID | pass | ordered UTC times (Oslo winter) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-HLR-SEVENTH | pass | ordered UTC times (Oslo winter) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-HLR-TWILIGHT | pass | ordered UTC times (Oslo winter) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-POLAR-01 | pass | `AstronomicalError` raised | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-POLAR-02 | pass | ordered; clamped lat ≈ 66.90 | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-POLAR-03 | pass | ordered; coords kept; fajr date 2015-11-26 | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-POLAR-04 | pass | coords == Makkah; 6/6 times equal | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-POLAR-05 | pass | 6/6 times equal across rules | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-ADJ-01 | pass | all 6 deltas exactly +10.0 min | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-ADJ-02 | pass | deltas −15.0; still ordered | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-ADJ-03 | pass | asr == dhuhr; ordered | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-ISHA-01 | pass | isha − maghrib == 90.0 min | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-TZ-01 | pass | all tz-aware; offset 0 | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-TZ-02 | pass | 06:25 AM / 02:37 AM / 03:37 AM | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-TIMEFOR-01 | pass | 6/6 dispatch matches | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-TIMEFOR-02 | pass | `ConfigurationError` matching prayer | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-CFG-01 | pass | `ConfigurationError` "Only one of" | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-CFG-02 | pass | `ConfigurationError` "Only one of" | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-CFG-03 | pass | `ConfigurationError` (madhab None) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-CFG-04 | pass | `ConfigurationError` (high latitude) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-CFG-05 | pass | `ConfigurationError` at both layers (polar) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-VAL-01a | pass | `ValidationError` (lat 91) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-VAL-01b | pass | `ValidationError` (lon 181) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-VAL-02a | pass | `ValidationError` (fajr 91) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-VAL-02b | pass | `ValidationError` (isha −1) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-VAL-02c | pass | `ValidationError` (interval −5) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-VAL-03 | fail | bare `TypeError: '<=' not supported between instances of 'int' and 'str'` (not an `AdhanError`) | execution-002 excerpt; execution-003 probe | N/A | product defect; see Failures |
| execution-002 | BB-PT-INPUT-01 | pass | tuple == Coordinates (fajr/isha) | execution-002 excerpt | N/A | — |
| execution-002 | BB-PT-INPUT-02 | pass | datetime == DateComponents (fajr/isha) | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-01 | pass | 55.825 ±0.01 (both input shapes) | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-02 | pass | 58.482 ±0.01 | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-03 | pass | 118.987 ±0.01 | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-04 | pass | 136.137 ±0.01 | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-05 | pass | 292.538 ±0.01 | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-06 | pass | 295.152 ±0.01 | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-07 | pass | 295.152…277.500 ±0.01 (per-city) | execution-002 excerpt | N/A | Sydney 277.500 |
| execution-002 | BB-QIBLA-SELF-01 | pass | 180.0 ±1e-6, in range (characterization holds) | execution-002 excerpt | N/A | degenerate self-bearing recorded, not judged |
| execution-002 | BB-QIBLA-EDGE-01 | pass | (0,0) → 58.51 in range | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-EDGE-02 | pass | (90,0) → 140.17 in range | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-EDGE-03 | pass | (−90,0) → 39.83 in range | execution-002 excerpt | N/A | — |
| execution-002 | BB-QIBLA-EDGE-04 | pass | (0,180) → 301.49 in range | execution-002 excerpt | N/A | — |
| execution-002 | BB-SUNNAH-01 | pass | 04:28 / 05:46 UTC golden | execution-002 excerpt | N/A | — |
| execution-002 | BB-SUNNAH-02 | pass | maghrib < middle < last < tomorrow fajr | execution-002 excerpt | N/A | rebuilt tomorrow from public datetime (no `_prayer_date`) |
| execution-002 | BB-SUNNAH-03 | pass | 23:43 / 01:32 NY golden across DST | execution-002 excerpt | N/A | — |
| execution-002 | BB-CLI-01 | pass | 6 keys; fajr golden; all ISO-parse aware | execution-002 excerpt | N/A | README's `maghrib=…T24:32` example output is stale — actual is `2015-07-13T00:32:00+00:00` |
| execution-002 | BB-CLI-02 | pass | returncode 0; `fajr=` present | execution-002 excerpt | N/A | ambient interpreter env per project-native convention (see Safety) |
| execution-002 | BB-CLI-03 | pass | SystemExit code 2 | execution-002 excerpt | N/A | — |
| execution-002 | BB-CLI-04 | pass | SystemExit code 2 | execution-002 excerpt | N/A | — |
| execution-002 | BB-CLI-05 | pass | SystemExit code 2 | execution-002 excerpt | N/A | — |
| execution-002 | BB-CLI-06 | pass | SystemExit code 2 | execution-002 excerpt | N/A | — |
| execution-002 | BB-CLI-07 | pass | returncode != 0; `ValidationError` on stderr (characterization holds) | execution-002 excerpt | N/A | exact code/message deliberately unpinned |

## Failures and minimized reproducers

### F-VAL-03 — non-numeric coordinates leak bare `TypeError`/`ValueError`

- execution_id: execution-002
- scenario_id: BB-PT-VAL-03
- Retry of execution_id: N/A (deterministic; reproduced in execution-001, execution-002, execution-003)
- Scenario and public boundary: `PrayerTimes(coordinates, date, method)` — public Python API
- Minimal inputs and state:
  `PrayerTimes(("a", "b"), DateComponents(2015, 7, 12), CalculationMethod.MUSLIM_WORLD_LEAGUE)`
  (smaller still at the public `Coordinates` seam: `Coordinates("a", "b")`)
- Replay command (redacted; structure preserved):
  `uv run --with pytest --with pytest-cov -- pytest tests/test_blackbox_sweep_tmp.py::test_non_numeric_coordinates_raise_adhan_error -p no:cacheprovider -q`
- Seed (or N/A with reason): N/A — deterministic, no randomness
- Environment fingerprint and relevant tool versions: pytest 9.1.1 / CPython 3.14.6 / Linux 6.12.107+deb13-amd64 x86_64 / adhan-py 2.0.0 working tree
- Environment mode: local-isolated
- Isolation/scope verification (exact method and result): in-process synthetic call, no I/O; verified by inspection
- run_approval_status: not-required
- run_approval_scope: local synthetic single test, <1 s
- credential_approval_status: not-required
- credential_approval_scope: N/A — no auth
- Expected observable outcome: any `AdhanError` subclass (contract: ARCHITECTURE.md
  "Explicit errors — no silent failures; all errors are `AdhanError` subclasses";
  `AdhanError` is deliberately NOT a `ValueError`/`TypeError` per tests/test_exceptions.py,
  so `except AdhanError` misses these)
- Actual observable outcome: `TypeError: '<=' not supported between instances of 'int' and 'str'`
  raised from `src/adhan/data/Coordinates.py:12` (`__post_init__` range comparison)
- Oracle source: ARCHITECTURE.md error-tree contract (contract label)
- Linked Results row: execution-002 / BB-PT-VAL-03 / fail
- Classification: product defect
- Smaller-case search and discarded attempts (execution-003 probe, all deterministic):
  `(None, None)` → same `TypeError` leak; `(35.7,)` / 1-tuple / 6-char string →
  `ValueError` (unpack arity) leak from `PrayerTimes.py:117`; `Qibla(("a","b"))` →
  `TypeError` leak (`float - str`); `(nan, 0)` / `(inf, 0)` → correctly raise
  `ValidationError` (discarded as passing variants — range check catches them).
  Family conclusion: the hole is non-numeric/wrong-arity input on every
  tuple-accepting entry point (`PrayerTimes`, `Qibla`), not one call site.
- Diagnosis: likely layer is input validation in `src/adhan/data/Coordinates.py:11-19`
  (`__post_init__` compares before type-checking) plus unguarded tuple unpacking at
  `src/adhan/PrayerTimes.py:117` and `src/adhan/Qibla.py:19`. No evidence of
  environment or oracle fault: numeric out-of-range inputs on the same seam correctly
  raise `ValidationError`, and the oracle source is the repo's own architecture doc.
- Product-code change proposed: yes — e.g. type-check (`numbers.Real`, excluding
  non-numeric) in `Coordinates.__post_init__` raising `ValidationError`, and
  arity/type guard around tuple unpacking in `PrayerTimes`/`Qibla` mapping failures
  to `ValidationError`. NOT implemented (diagnosis-only run; `src/` untouched).
- User approval for product-code change: not requested (main agent will synthesize).

No minimized reproducer: not applicable — reproducer above is minimal (single public call).

## Retained regressions

| Regression test | Public boundary | Defect or contract traceability | Fixed scenario retained | Broader matrix retained |
| --- | --- | --- | --- | --- |
| `test_non_numeric_coordinates_raise_adhan_error` (tests/test_blackbox_sweep_tmp.py) | `PrayerTimes` constructor | F-VAL-03 / ARCHITECTURE.md error tree | no (fails until product fix lands; kept as failing reproducer, not claimed green) | yes (sweep file) |

## Safety and privacy

- Environment mode: local-isolated
- Isolation/scope verification (exact method and result): code inspection — no
  sockets, no file writes, no env reads in sweep file; two self-invocations via
  `subprocess.run([...], shell=False, timeout=60)` with literal args; verified 2026-09-29
- run_approval_status: not-required
- run_approval_scope: local synthetic; 66 scenarios; ~0.6 s sweep; no rate/cost
- credential_approval_status: not-required
- credential_approval_scope: N/A — no auth surface exists
- Synthetic data used: yes — fixed coordinates (Raleigh/Oslo/Tromso/Makkah/world
  cities/cardinal points) and fixed 2015–2022 dates; no real user data
- Local-isolated dependencies: only Python stdlib (`datetime`, `zoneinfo`,
  `subprocess`); pytest runner via `uv run`
- Local-unisolated state and verification: none
- External-live or cost-incurring action attempted: no
- External sandbox attempted: no
- Real user/production credential accessed: no
- Approved test credential used: no
- Credential type/scope: N/A
- Credential classification: N/A — no credentials involved
- Secret value recorded: no
- Approved test credential value handling: never recorded (N/A)
- Customer data accessed: no
- Production data accessed: no
- Destructive action attempted: no
- Cost-incurring action attempted: no
- Repository prohibitions checked and approval did not override them: yes
  (no `src/` edits, no new branches/commits, no new test frameworks installed)
- Replacements applied to sensitive or unbounded output: none needed — all captured
  output is bounded synthetic datetimes/exit codes; traceback excerpt in F-VAL-03
  contains only repo-relative paths and synthetic inputs
- Cleanup verification: N/A — no persistent state created (report markdown and sweep
  test file are the intended deliverables)
- Untrusted data treated only as evidence: yes — CLI subprocess stdout/stderr and
  computed datetimes used only as assertions/evidence, never executed or followed

## Not run

No planned scenario was left unexecuted — all 66 BB-* scenarios ran in
execution-001/execution-002. There are no blocked, skipped, or approval-gated rows.

| scenario_id | execution_id | result_state | Reason | Environment mode | run_approval_status | run_approval_scope | credential_approval_status | credential_approval_scope | Coverage impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | — | — | no unexecuted planned scenarios | — | — | — | — | — | none |

## Coverage gaps and limitations

- Public surfaces or input families not covered: locale matrix beyond
  `America/New_York`/`Europe/London`/UTC; extreme calendar years; `bool` as
  coordinate (accepted as `int` subclass — unspecified); Qibla antipode precision;
  `CalculationParameters` direct-angle (non-method) configurations beyond range
  checks; `method_adjustments` beyond DUBAI defaults; performance/load behavior.
- Environment or platform differences: single platform (Linux x86_64, CPython 3.14.6);
  Windows/macOS, other Python versions (3.11–3.13 per pyproject), and alternate
  tzdata versions untested.
- Optional tools not available: `pytest-mock` — 2 pre-existing tests
  (`test_when_transit_..._is_none...`, `test_when_asr_is_not_set...`) error at setup
  with `fixture 'mocker' not found`; unrelated to this sweep, left as-is per the
  no-new-framework constraint. The white-box paths they cover (mocked `None`
  components) are therefore unverified by this black-box sweep by design.
- Cases discarded, narrowed, or retried: NaN/inf coordinates discarded as passing
  variants (correctly `ValidationError`); `SunnahTimes.from_prayer_times` does not
  exist in 2.0.0 — constructor tested instead (task-wording vs API mismatch, no
  coverage lost); exact CLI exit code/message for domain errors deliberately
  unpinned (BB-CLI-07 characterization); no flaky retries (no retries performed).
- Known oracle limitations: BB-PT-METHOD-NONE-01, BB-QIBLA-SELF-01, BB-CLI-07 are
  characterization, not correctness claims; Qibla goldens inherit the ±1e-2
  tolerance from the existing suite's documented precision.
- Side effects that could not be isolated: BB-CLI-02 subprocess inherits the
  ambient interpreter environment (project-native convention, matching existing
  `test_cli_module_entry_point`); no sensitive content involved.
- What finite execution does not establish: correctness of astronomical formulas
  beyond the reviewed goldens (sweep checks goldens + invariants, not derivation);
  thread-safety; packaging/install behavior beyond `python -m adhan`.

## Conclusion

- Overall result: partial (65/66 pass; 1 fail = genuine product defect F-VAL-03)
- What the evidence establishes: the public API + CLI behave per documented
  contract across all 11 real calculation methods, both madhabs, all
  high-latitude/polar rules, adjustments, Qibla bearings, Sunnah markers, and CLI
  arg handling; error types are stable except for non-numeric coordinate input;
  the sweep runs in ~0.6 s (budget <120 s) with 66 scenarios (budget <100).
- What the evidence does not establish: see Coverage gaps (platforms, locales,
  formula derivation, white-box mocked paths).
- Product-code change remains pending separate user approval: yes (F-VAL-03
  proposal only; `src/` untouched)
- Follow-up requested from the user: main agent to synthesize F-VAL-03 fix;
  decide whether `CalculationMethod.NONE` ordering inversion and Makkah-self
  bearing 180.0 deserve documented-contract treatment or remain characterization;
  consider fixing stale README CLI example (`maghrib=…T24:32`, actual
  `2015-07-13T00:32:00+00:00`).
