# Parameterized testing evidence report

## Scope

- Target behavior or public boundary: `PrayerTimes`, `Coordinates`,
  `CalculationParameters`, `Qibla`, `SunnahTimes` (public API in
  `src/alfalak/__init__.py`, al-falak 2.0.0, offline prayer-times library).
- Consumer and contract: library consumers calling the public constructors;
  contract is the quantified properties P1–P6 below plus documented stable
  errors (`ValidationError`, `AstronomicalError`, `ConfigurationError`).
- Requested focus and broad-coverage exclusions: pre-release feasibility sweep
  through the real public boundary. Excluded: CLI (`__main__`), astronomy
  internals, `time_for_prayer`/`current_prayer` conveniences. Recorded
  narrowing: `CalculationMethod.NONE` excluded from generated ordering-class
  batteries (degenerate zero-angle config; covered by characterization test).
- Valid domain: lat [-90, 90], lon [-180, 180], all documented methods,
  Shafi/Hanafi, all high-latitude rules, all polar-circle rules, adjustments
  [-60, 60], fajr/isha angles [1, 30], dates incl. leap day 2024-02-29,
  equinox 2024-03-20, solstices, US/EU DST boundaries.
- Invalid domain: numeric out-of-range lat/lon/angles/interval, NaN/±inf;
  expected `ValidationError` plus no global state mutation.
- Unsupported domain: polar day/night with `PolarCircleRule.NONE` (expected
  `AstronomicalError`); `madhab=None` / method+params together (expected
  `ConfigurationError`); exact-pole `NEAREST_DAY` (defect D1, xfail).
- Environment-dependent domain: polar resolution outcomes, `ZoneInfo`
  conversions (system tzdata), DST-transition Sunnah markers.
- Property statements and quantified invariants:
  - P1 (order): for every valid input with a documented method and zero
    adjustments, `fajr<=sunrise<=dhuhr<=asr<=maghrib<=isha`, UTC, minute-aligned.
  - P2 (metamorphic): Hanafi Asr >= Shafi Asr, all else equal.
  - P3 (metamorphic): single-prayer adjustment of k minutes shifts exactly
    that prayer by k minutes, others unchanged.
  - P4 (state-transition): out-of-range numerics raise `ValidationError`;
    method templates and fresh-instance behavior unchanged afterwards.
  - P5 (invariant): Qibla direction in [0, 360).
  - P6 (derivation): `maghrib < middle < last_third < tomorrow fajr` and
    `(last_third - middle) == night/6` within ±60 s rounding tolerance.
- Coverage plan and input families: fixed goldens first (Raleigh
  second-precision, +10 min offsets, Oslo moon-sighting, Umm-al-Qura interval,
  7 Qibla bearings, Sunnah golden + DST golden, rejection goldens), then
  seeded generated witnesses stratified across methods/madhabs/high-lat
  rules/polar rules/boundary latitudes/dates. Case-matrix planner
  (`scripts/plan_case_matrix.py`, seed 20260929, sample 48) used for planning
  only; execution is project-native pytest with `random.Random` generators.
- Finite samples are not exhaustive proof: yes.

## Runner and environment

- Project-native runner and version: `uv run --with pytest --with pytest-cov
  -- pytest -q` (pytest 9.1.1, pytest-cov 7.1.0).
- Relevant dependency/tool versions, including Hypothesis when used:
  Hypothesis NOT used (not in `requirements.txt`; deterministic stdlib
  fallback per skill — reduced guarantees: finite witnesses, manual
  minimization, no automatic shrinking). Hypothesis 6.168.3 is installable via
  `uv run --with hypothesis` but was deliberately not added to the run.
- Working directory (project-relative or redacted): repo root (branch
  `chore/blackbox-param-feasibility-20260929`).
- Environment fingerprint: Ubuntu Linux, Python 3.13.5, system tzdata,
  `TZ=+08` ambient (all generated assertions use explicit UTC/`ZoneInfo`,
  no ambient-TZ dependence).
- Seed and generator: `SEED = 20260929`, `random.Random(SEED + stream)` per
  battery (streams 0–5); fully deterministic — two consecutive runs produced
  identical results.
- Unicode replay evidence: N/A (no Unicode families in scope; malformed-input
  battery uses wrong-type scalars, not text forms).
- Controlled clock, UUID source, and other nondeterminism: no clocks/UUIDs in
  scope; dates are fixed `DateComponents`.
- Normalization rules: none needed (UTC datetimes compared directly;
  minute-rounding asserted as `second == 0 and microsecond == 0`).
- Case budget: count <=200 generated + 26 fixed (222 total) / time <120 s
  (actual ~1 s) / input size scalars only / memory negligible / rate N/A
  (offline) / cost zero.
- Approval status: no live/destructive/cost-incurring work; none needed.
- Synthetic data and isolation: all inputs synthetic; no network, no secrets,
  no prod data; `src/` untouched (`git diff HEAD -- src/` empty).
- Optional tools unavailable: Hypothesis (by choice, disclosed above);
  `pytest-mock` absent from required runner (2 pre-existing `mocker` errors
  in `tests/test_PrayerTimes.py`, unrelated to this sweep).
- Report date: 2026-09-29.

## Plan and counts

- Fixed-example count: 26 (7 goldens + 7 Qibla goldens + 12 rejections).
- Generated-witness count: 191 (48 ordering + 20 madhab + 20 adjustments +
  25 qibla + 16 sunnah + 30 polar + 20 invalid/mutation + 12 angles).
- Invalid-witness count: 19 rejection witnesses + 1 no-mutation test.
- Unsupported-witness count: 6 polar-NONE + 2 config-error + 5 xfail defects.
- Discarded-case count and reasons: 2 (exact-pole × NEAREST_DAY combos
  removed from the polar battery and promoted to dedicated strict-xfail
  defect tests D1 — Superset coverage, not loss).
- Truncated: no.
- Truncated count: 0.
- Truncation reason, budget, and coverage impact: N/A.
- Cases or families not run: southern exact pole in-suite (probed manually,
  fails identically — recorded under D1); `time_for_prayer` API;
  `CalculationMethod.NONE` in ordering batteries (narrowed, characterization
  instead); non-UTC `time_zone` variants beyond the DST golden; concurrent/
  multi-locale runs.

## Properties, oracles, and cases

| case_id | domain | input class | property or invariant | named oracle | expected result or error | expected state/effects | fixed/generated | evidence reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F-GOLDEN (7 tests) | valid | goldens | P1 + exact output | reviewed golden timestamps | exact UTC times | none | fixed | tests/test_parameterized_sweep_tmp.py::TestFixedGoldens |
| F-CHAR-ZERO-ANGLE | valid-degenerate | zero angles | characterization (open question) | observed behavior | fajr>sunrise, isha<maghrib | none | fixed | same, test_zero_angle_ordering_characterization |
| F-QIBLA (7) | valid | goldens | P5 + exact output | reviewed bearings ±1e-2 | approx match | none | fixed | test_qibla_goldens |
| F-REJECT (12) | invalid/unsupported | rejections | P4 + stable errors | documented error type | ValidationError/ConfigurationError/AstronomicalError | none | fixed | TestFixedRejections |
| G-ORD-000..047 | valid | ordering battery | P1 | sorted-order + UTC + minute-aligned | ordered | none | generated | TestGeneratedOrdering |
| G-MAD-000..019 | valid | madhab pairs | P2 | differential Hanafi>=Shafi | holds | none | generated | TestGeneratedMadhab |
| G-ADJ-000..019 | valid | single adjustment | P3 | exact timedelta shift | exact | none | generated | TestGeneratedAdjustments |
| G-QIB-000..023 | valid | qibla sample | P5 | range check | in [0,360) | none | generated | TestGeneratedQibla |
| G-SUN-000..015 | valid | sunnah sample | P6 | ordering + night/6 spacing | holds ±60 s | none | generated | TestGeneratedSunnah |
| G-POL-000..029 | env-dependent | polar rules | P1 or stable error | ordering / AstronomicalError | holds or raises | none | generated | TestGeneratedPolar |
| G-INV / G-MAL | invalid | numeric/malformed | P4 / characterization | ValidationError / builtin error | raises; templates unchanged | none | generated | TestGeneratedInvalid |
| G-ANG-000..011 | valid | custom angles | P1 + monotonicity | ordering / wider-angle-earlier-fajr | holds | none | generated | TestGeneratedAngles |
| D1 (4, xfail) | env-dependent | exact pole NEAREST_DAY | P1 (violated) | ordering after resolution | xfail: AstronomicalError raised | none | generated-fixed | test_nearest_day_exact_pole_known_defect |
| D2 (1, xfail) | valid | 89.1N equinox | P1 (violated) | sorted order | xfail: asr>maghrib | none | fixed (minimized) | test_asr_spill_past_maghrib_known_defect |

## Exact executions

| execution_id | case_ids | working directory | exact command | replay note | exit status | runner | environment | bounded evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| execution-001 | all 222 | repo root | `uv run --with pytest --with pytest-cov -- pytest -q tests/test_parameterized_sweep_tmp.py` | initial run | 7 failed | pytest 9.1.1 | Python 3.13.5, TZ +08 | 7 failures (4 NONE-ordering, 1 zero-angle anchor, 2 polar NEAREST_DAY) |
| execution-002..004 | probes | repo root | `uv run --with pytest -- python - <<EOF (probe heredocs)` | minimization/diagnosis probes | 0 | python | same | root causes isolated (see failures) |
| execution-005 | all 222 | repo root | same as execution-001 | after oracle correction | 217 passed, 5 xfailed | pytest 9.1.1 | same | green with documented xfails |
| execution-006 | all 222 | repo root | same as execution-001 | determinism replay | identical: 217 passed, 5 xfailed | pytest 9.1.1 | same | deterministic |
| execution-007 | full suite | repo root | `uv run --with pytest --with pytest-cov -- pytest -q -p no:cacheprovider` | regression check | 1 failed (parallel agent file), 2 pre-existing mocker errors | pytest 9.1.1 | same | src/ untouched; no interference from this sweep |

## Results

| case_id | execution_id | result state | observed outcome | oracle result | evidence reference | retry of | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 26 fixed | execution-005 | pass | all goldens/rejections match | oracle holds | sweep file | execution-001 (1 bad anchor corrected) | zero-angle anchor converted to characterization |
| G-ORD (48) | execution-005 | pass | ordered, UTC, minute-aligned | P1 holds | sweep file | 4 failures re-scoped | NONE excluded (recorded narrowing) |
| G-MAD (20) | execution-005 | pass | Hanafi>=Shafi | P2 holds | sweep file | — | — |
| G-ADJ (20) | execution-005 | pass | exact shifts | P3 holds | sweep file | — | — |
| G-QIB (25) | execution-005 | pass | all in [0,360) | P5 holds | sweep file | — | — |
| G-SUN (16) | execution-005 | pass | ordering + night/6 spacing | P6 holds | sweep file | — | — |
| G-POL (30) | execution-005 | pass | NONE raises; others ordered | holds | sweep file | 2 moved to D1 xfails | — |
| G-INV/G-MAL (20) | execution-005 | pass | ValidationError; malformed->TypeError/ValueError | P4 + characterization | sweep file | — | string/None coords raise TypeError, NOT ValidationError |
| G-ANG (12) | execution-005 | pass | ordered; monotonic fajr | holds | sweep file | — | angles sampled in [1,30] |
| D1 (4) | execution-005 | expected-failure | AstronomicalError, no resolution | violated (defect) | xfail strict | execution-001 failures | product defect, fix proposed, not implemented |
| D2 (1) | execution-005 | expected-failure | asr 22:12 > maghrib 21:22 | violated (defect) | xfail strict | minimized from battery-adjacent probe | product defect, fix proposed, not implemented |

## Failures and minimized reproducers

### Failure D1 — NEAREST_DAY unresolvable at exact poles

- Original case and exact generated input: `G-POL-026/030` —
  `PrayerTimes((90.0, 0.0), DateComponents(2024, 6, 21) / (2024, 12, 21))`
  with `CalculationMethod.MUSLIM_WORLD_LEAGUE`,
  `polar_circle_rule=NEAREST_DAY`.
- Boundary and public consumer: `PrayerTimes` polar path, library consumer.
- Original seed, state, clock, UUID source, environment, normalization: seed
  20260929 battery; stateless; UTC; no normalization.
- Original failure, expected result, and observed result: expected resolution
  per rule docstring ("nearest date on which the sun rises and sets");
  observed `AstronomicalError: No date with sunrise/sunset found within a year.`
- Original replay command: `uv run --with pytest --with pytest-cov --
  pytest -q tests/test_parameterized_sweep_tmp.py` (then xfail test directly).
- Original command exit status: 1 (in execution-001).
- Minimized input and state: identical (already minimal: exact pole, any
  solstice date, any method — south pole `-90.0` probed, fails identically).
- Minimized replay command: `uv run --with pytest --with pytest-cov --
  pytest -q tests/test_parameterized_sweep_tmp.py -k nearest_day_exact_pole`.
- Minimization method, discarded attempts, and shrinking status: manual —
  varied lat (89.0/89.5/89.9/89.99/90.0), both poles, both solstices, all
  other rules (NEAREST_LATITUDE/MAKKAH resolve fine at 90.0). Failure onset:
  somewhere in (89.5, 89.9]; 89.5 resolves (but see D2), 89.9+ never does.
  No auto-shrinking (no Hypothesis) — manual binary narrowing only.
- Product defect / bad oracle / environment issue / flake classification:
  product defect (edge). Root cause: at |lat|→90°, cos(lat)→0 makes the
  hour-angle argument singular, so `_schedule_defined` is False for every
  probed date and `_nearest_date_with_sunrise_sunset` exhausts the year.
- Original failure retained: yes (as strict-xfail regression).
- Minimized failure retained: yes
  (`test_nearest_day_exact_pole_known_defect`, ±90 × 2 dates).
- Retained fixed regression: yes (same).
- Broader property or matrix retained: yes (G-POL battery minus these combos).
- Product-code change proposed: yes — special-case |lat|==90 (or clamp the
  cos-latitude divisor / fall back to NEAREST_LATITUDE) in the NEAREST_DAY
  path; alternatively document exact poles as unsupported for NEAREST_DAY.
- Separate user approval for a product-code change: not requested (diagnosis
  only; `src/` untouched).

### Failure D2 — Asr spills past Maghrib near the polar boundary

- Original case and exact generated input: discovered while minimizing polar
  behavior — `PrayerTimes((89.5, 0.0), DateComponents(2024, 6, 21),
  CalculationMethod.MUSLIM_WORLD_LEAGUE)` with NEAREST_DAY resolved to
  2024-03-18 with asr on 2024-03-19 05:44 > maghrib.
- Boundary and public consumer: `PrayerTimes._set_asr`, library consumer.
- Original seed/state/env: deterministic; stateless; UTC.
- Original failure, expected result, and observed result: expected
  fajr<=…<=isha; observed `asr (03-19 05:44) > maghrib (03-18 20:21)`.
- Original replay command: probe heredoc (execution-002..004 class).
- Original command exit status: assertion failure in probe.
- Minimized input and state: `PrayerTimes((89.1, 0.0),
  DateComponents(2024, 3, 19), CalculationMethod.MUSLIM_WORLD_LEAGUE)` — no
  polar rule involved (schedule defined; default rule is a no-op):
  asr 22:12 > maghrib 21:22, same calendar day. Onset hunt: 89.0 ordered,
  89.1 violated (threshold in between).
- Minimized replay command: `uv run --with pytest --with pytest-cov --
  pytest -q tests/test_parameterized_sweep_tmp.py -k asr_spill`.
- Minimization method: manual latitude bisection (85→87→88→88.5→89→89.1) on
  the resolved equinox date, then dropped the polar rule entirely once the
  direct trigger was found.
- Classification: product defect (edge, high-latitude). Root cause: near the
  polar boundary the shadow-length hour angle exceeds the short day, so
  `afternoon()` lands past sunset; `_set_asr` clamps only the dhuhr side
  (`asr < dhuhr → asr = dhuhr`, `PrayerTimes.py:315`) with no maghrib-side
  guard. Same code shape as upstream adhan ports — fix direction needs a
  product decision (clamp vs. documented limitation).
- Original failure retained: yes (strict-xfail regression with locked
  asr/maghrib values).
- Minimized failure retained: yes.
- Retained fixed regression: yes (`test_asr_spill_past_maghrib_known_defect`).
- Broader property or matrix retained: yes (P1 battery).
- Product-code change proposed: yes — clamp `asr` to `<= maghrib` (mirror of
  the dhuhr clamp) or document high-latitude Asr spill as a known limitation.
- Separate user approval: not requested (diagnosis only).

### Corrected bad oracles (not product defects)

- B1: equality anchor `fajr == sunrise` at angle 0 — wrong oracle. Sunrise
  uses the −50/60° solar-altitude convention (`SolarTime.py:29`) while
  `hour_angle(0)` uses depression 0, so fajr (10:13) > sunrise (10:08) is the
  designed arithmetic, and isha (00:28) < maghrib (00:32) symmetrically.
  Converted to a characterization test locking observed behavior as an open
  question; `CalculationMethod.NONE` excluded from generated ordering-class
  batteries with recorded reason.
- B2: initial G-ORD failures (4 cases, all method NONE) — same root cause as
  B1; resolved by the documented narrowing, not by touching product code.

## Safety and privacy

- Synthetic data used: yes — all coordinates/dates/angles fabricated.
- Local-isolated dependencies and state: yes — offline library, no I/O.
- External or live target used: no.
- Real secrets, live credentials, customer data, or production data used: no.
- Approval never authorized secret or data access: yes (N/A, nothing requested).
- Destructive action attempted: no.
- Cost-incurring action attempted: no.
- Untrusted output treated only as evidence: yes.
- Redactions and bounded-capture method: N/A (no sensitive values exist).
- Secret values recorded: no.
- Raw sensitive output recorded: no.

## Not run and skips

| case_id or coverage area | result state | reason | command | exit status | coverage impact |
| --- | --- | --- | --- | --- | --- |
| south-pole in-suite D1 | not-run | probed manually only (fails identically) | N/A | N/A | negligible (symmetric singularity) |
| `time_for_prayer` / CLI | not-run | out of scope (boundary = constructors) | N/A | N/A | convenience wrappers untested |
| non-UTC `time_zone` variants | not-run | one DST golden covers TZ path | N/A | N/A | TZ conversion matrix gap |
| `tests/test_PrayerTimes.py` mocker tests | not-run (error) | `pytest-mock` absent from required runner; pre-existing | `uv run … pytest -q` | error (fixture 'mocker' not found) | none for this sweep |
| parallel agent file failure | not-run | `test_blackbox_sweep_tmp.py::test_non_numeric_coordinates_raise_alfalak_error` belongs to the parallel agent; corroborates G-MAL characterization (TypeError, not AlFalakError) | N/A | N/A | none; do not touch |

## Limitations and conclusion

- What the executed fixed and generated cases establish: P1 holds across 48
  seeded combos (11 methods × 3 high-lat rules × boundary/mid latitudes ×
  8 dates) plus 30 polar and 12 custom-angle witnesses; P2/P3 hold on 20
  witnesses each; P4 holds for 19 invalid witnesses with template/instance
  immutability verified; P5 holds on 31 bearings; P6 holds on 16 witnesses.
- What finite samples do not establish: exhaustive proof — 196 generated
  witnesses with no automatic shrinking; southern-hemisphere high-latitude
  and non-UTC timezone matrices are thin.
- Oracle and normalization limitations: P6's spacing check reuses UTC
  arithmetic adjacent to the implementation (independent tolerance, but
  adjacent derivation); zero-angle/NONE behavior locked as characterization,
  not contract; malformed-type oracle is characterization (TypeError/
  ValueError, not AlFalakError).
- Environment and platform limitations: single run, Ubuntu, Python 3.13.5,
  system tzdata, TZ=+08 ambient (neutralized by explicit UTC/ZoneInfo).
- Coverage gaps and discarded/truncated families: as listed in Not run; no
  truncation; 2 battery combos promoted to D1 xfails (coverage retained).
- Follow-up or diagnosis-only next steps: product decision on D1 (fallback
  or documented-unsupported) and D2 (maghrib-side Asr clamp or documented
  limitation); both need separate approval before any `src/` change.
- Overall result: partial (green suite with 5 expected-failure defect
  regressions: 217 passed, 5 xfailed).
- Product-code change remains pending separate approval: yes.
