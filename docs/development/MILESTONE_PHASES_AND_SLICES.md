# Al-Falak Milestone Phases and Implementation Slices

Source: `docs/development/MILESTONES.md` (6 phases).
Codebase snapshot: `src/alfalak/` (30 `.py` files incl. 5 `__init__.py`, + `py.typed`),
`tests/` (21 `.py` files = 20 test modules + `support.py`), `CHANGES.md` 1.0.0 (2026-09-30).
This document breaks each phase into single-PR-sized slices, marks what is already
implemented (with location + completeness), corrects wrong/ambiguous readings of the
milestone table, and expands missing features. Deliberately **not** scoped down to the
current architecture — the architecture is allowed to change.

> Fact-check pass 2026-10-02: every external claim below was checked against primary
> sources (Meeus 2nd ed. / Willmann-Bell 1998; Yallop NAO TN No.69 1997; Odeh
> *Exp. Astron.* 18:39–64; PrayTimes.org; Fiqh Council NA; moonsighting.com;
> BatoulApps Adhan ports; NOAA/NCEI; IANA theory docs). Corrections from that pass
> are marked **[FC 2026-10-02]** inline where they reverse a previous reading of
> this document (most visibly: Neo-MABIMS is 3°/6.4°, not 4°/6.4°; the dip
> coefficient is 0.0293 not 0.0347; spherical-vs-ellipsoidal Qibla error reaches
> ~0.34°, not <0.1°; 7-dp Kaaba coordinates are false precision).

## Status legend

- **DONE** — fully implemented, only maintenance/verification work remains.
- **PARTIAL** — implemented but incomplete vs. the milestone row (gap described).
- **TODO** — not present in `src/` (verified by read + grep, 2026-10-02).
- **EXTRA** — implemented in code but not mentioned in the milestone row (worth keeping).

Meeus citations below pin the **2nd edition (Willmann-Bell, 1998)** unless noted:
JD = Ch.7; interpolation = Ch.3 (p.23–24); sidereal/transit/rise-set = Ch.12/15
(pp.87/101–102); nutation/obliquity = Ch.22 (p.143ff); solar coordinates = Ch.25
(p.163ff); equation of time = **Ch.28, p.183** (Ch.27 in the 1st ed. — always state
the edition); Moon position = **Ch.47 only** (Ch.45–46 are Saturn — earlier drafts
of this doc wrote "Ch.45–47", which is wrong).

---

## Phase 1 — Core Mathematical Foundation & Spatial Geodesy

### Current state

| Milestone claim | State | Evidence |
|---|---|---|
| Gregorian → JD conversion | **DONE** | `src/alfalak/astronomy/CalendricalHelper.py:4-20` (`julian_day`, Meeus Ch.7 Gregorian branch, `B = floor(2 − A + A/4)`), `julian_century` at `:23-25` (J2000.0 epoch `2451545.0 / 36525`, Ch.25 p.163). |
| Angle normalization & spherical trig helpers | **DONE** | `src/alfalak/util/FloatUtil.py:4-16` (`unwind_angle` → `[0,360)`, `closest_angle` → `(−180,180]`); `src/alfalak/astronomy/Astronomical.py:103-111` (`altitude_of_celestial_body`, Ch.13 p.93: `sin h = sin φ sin δ + cos φ cos δ cos H`), `:114-186` (transit/hour-angle/interpolation, Ch.3 p.24 / Ch.15 p.102). |
| Qibla bearing | **PARTIAL** | `src/alfalak/Qibla.py:32-41` — spherical initial-bearing via `atan2` (four-parts formula, Todhunter "Spherical Trigonometry" p.50, ported from adhan-kotlin, which is itself a port of BatoulApps adhan-java). Bearing-only, spherical-Earth assumption, no distance output. |
| High-precision great-circle (Vincenty **or** Haversine) + WGS84 | **TODO** | Zero hits in `src/` for `Vincenty|WGS84|ellipsoid|haversine|geodesic|Karney`. Only prose mentions: `MILESTONES.md` Phase-1 row and a validation comment in `tests/test_qibla.py:21`. |
| Magnetic declination hooks (True vs Magnetic North) | **TODO** | Zero hits in `src/` for `magnetic|WMM|IGRF|compass|variation` (only solar `declination` in `SolarCoordinates.py:31`). Only mention is `MILESTONES.md` Phase-1 row. |
| Kaaba constants 21.4225°N 39.8262°E | **PARTIAL** | Code carries *more* digits than the milestone: `Qibla.py:6` `MAKKAH = Coordinates(21.4225241, 39.8261818)`; docs round to 4 dp (`docs/user/qibla.md:55`). No single canonical-constants module; constant lives in `Qibla.py`. **[FC 2026-10-02]** the extra digits are *false precision* (see correction 3) — the milestone's 4 dp is the honest value. |
| `Coordinates` validation | **EXTRA / DONE** | `src/alfalak/data/Coordinates.py:9-33` — rejects bool/non-Real/Decimal, enforces lat ∈ [−90,90], lon ∈ [−180,180], stores plain floats post-validation. |

### Corrections / clarifications to the milestone row

1. **"Vincenty formula or high-precision Haversine" is a category error.** Vincenty
   (1975) is an *iterative ellipsoidal* inverse solver; Haversine is a *spherical*
   closed form. They are not interchangeable options for one slot. The phase needs
   three distinct deliverables: (a) spherical bearing (exists), (b) spherical distance
   (missing — trivially derivable but absent), (c) ellipsoidal inverse
   (WGS84 + Karney/GeographicLib as primary — Karney, *J. Geodesy* 87:43–55, 2013,
   converges always at ~15 nm accuracy; Vincenty is documented non-convergent for
   nearly-antipodal points and is kept only as a legacy fallback with rationale, or omitted).
2. **"WGS84 geodetic reference models" is vague.** Pin to: WGS84 *defining* constants
   (`a = 6378137.0 m` exact, `f = 1/298.257223563` exact; `b = 6356752.31424518 m`,
   `e² = 0.00669437999014` are *derived*, label them as such), inverse problem
   (forward azimuth + distance), and a stated accuracy target (e.g. mm-level
   agreement with the Karney reference implementation).
3. **[FC 2026-10-02] Kaaba precision: 4 dp is canonical, 7 dp is surveying theater.**
   The prior draft of this doc recommended stating 7 dp. That was wrong: the Kaaba
   is a ~13 m building with no published cm-level geodetic survey; the value in code
   is a web-map pin rounding (cf. latlong.net `21.422487, 39.826206`; QiblaLocator/
   AdhanLive cite 4 dp `21.4225 N, 39.8262 E`). 1e-7° ≈ 11 mm at the equator —
   physically meaningless for a building centroid. Keep the code constant for compat,
   but state the canonical location at **4 dp (≈11 m)** or at most 5 dp (≈1 m), and
   document 7 dp as display rounding only.
4. **J2000.0 is already load-bearing** (`julian_century`, obliquity/nutation series in
   `Astronomical.py:6-100`) — the milestone reads as if epoch handling is new work.
   J2000.0 = JD 2451545.0 TT = 2000-01-01 12:00 TT (USNO). Remaining epoch work is
   precession/nutation documentation, not plumbing. Note the 4-term nutation
   truncation (`Astronomical.py:69-84`, Meeus Ch.22 low-accuracy series) leaves
   ~0.5–1″ residual → <0.3 s in time: negligible for prayer times, document and move on.
5. **[FC 2026-10-02] Spherical-vs-ellipsoidal Qibla error is NOT sub-arcminute.**
   The prior draft claimed "< ~0.1° worst case". Published comparisons show typical
   differences of a few arcminutes and maxima of ~20′ (~0.34°) (IJRS great-circle
   study: up to 20′26″; Walisongo/Al-Hilal: ~8′ vs Vincenty on tested legs; Barmore
   thesis: spherical azimuths "do not represent the real case with an accuracy
   approaching a minute of arc"). State: typical few arcmin, worst-case ~0.3–0.35°,
   growing near the antipode. Slice 1.3/1.7 tolerances below are updated accordingly.
6. **Gregorian-only JD needs a stated cutoff.** Meeus Ch.7 handles both branches
   (`B = 2 − A + ⌊A/4⌋` Gregorian, `B = 0` Julian; reform gap 1582-10-04 Julian →
   1582-10-15 Gregorian). All operational prayer dates are ≫1582, so the missing
   Julian branch never triggers — but the limitation (pre-1582 error ≈ 10 days) must
   be asserted in a test, not discovered by a historian.

### Slices

#### 1.1 — JD / Julian-century golden tests (DONE, harden only)
State: **DONE**. `CalendricalHelper.py:4-25` + `tests/astronomy/` coverage.
Remaining single-PR work: lock Meeus worked-example goldens (e.g. 2000-01-01 12:00 TT =
2451545.0) and a Gregorian-reform-boundary documented limitation (no Julian-calendar
branch — currently Gregorian-only, which is correct for prayer use but should be asserted
with the 1582-10-04 → 1582-10-15 gap noted).

#### 1.2 — Angle helpers property tests (DONE, harden only)
State: **DONE**. `FloatUtil.py:4-16`.
Remaining: invariant tests (`unwind_angle` idempotence/range, `closest_angle` round-trip)
— small PR, no production change.

#### 1.3 — Qibla bearing: document + lock (PARTIAL → DONE)
State: **PARTIAL** (works, under-specified).
PR: move `MAKKAH` into a canonical constants module (keep re-export from `Qibla.py`
for compat), state spherical-assumption + published error bound vs. ellipsoidal
(typical few arcmin, worst-case ~0.3–0.35° per correction 5 — **do not** assert
<0.1°), add antipode/degenerate tests. Note the two distinct degeneracies:
Makkah-to-self `atan2(0,~0)` (characterized in `tests/test_blackbox_sweep.py:537-544`,
observed 180.0 — contract is "float in [0,360), no raise") vs. the *true antipode*
≈ (−21.4225, −140.17), South Pacific near Tematagi atoll, where every azimuth is
equidistant and any bearing is defensible. Lock 7-city goldens already in
`tests/test_qibla.py:1-39` (`pytest.approx abs=1e-2`).
Acceptance: bearing API unchanged; constants importable from one place; both
degenerate behaviors documented (not raising).

#### 1.4 — Qibla distance (spherical) (TODO)
New `Qibla.distance_to_makkah_km` (or free function) via central-angle
(`atan2`-form, numerically stable — **not** naive law-of-cosines). Pin the radius:
`R = 6371.0088 km` (IUGG mean radius `R₁ = (2a+b)/3`; note 6371.0/6378.137 variants
shift results ~0.1–0.3%).
Files: `Qibla.py`, `tests/test_qibla.py`.
Acceptance: goldens for 3+ cities (e.g. Kuala Lumpur ~6600 km, New York ~10300 km,
Sydney ~13200 km, ±10 km tolerance documented); antipode returns ~20015 km, no NaN.

#### 1.5 — Ellipsoidal inverse on WGS84 (TODO)
New module (e.g. `astronomy/Geodesy.py`): Karney-quality inverse (vendored or
dependency-free implementation — no new runtime deps per `ARCHITECTURE.md:97`),
WGS84 defining constants (correction 2), returning forward azimuth + distance.
Vincenty kept only as documented fallback or omitted with rationale
(non-convergence near antipodes). Spherical bearing stays default;
ellipsoidal exposed as opt-in (`method="ellipsoidal"`).
Acceptance: agreement with GeographicLib reference to ≤1e-6 deg / ≤1 m on test set
including a near-antipodal case; convergence failure raises `AstronomicalError`
with diagnostics (follow `PrayerTimes.py:80-85` precedent — note: Karney converges
by construction, so the guard is defensive, not a "60-iteration" Vincenty loop).

#### 1.6 — Magnetic declination hooks (TODO)
**Not** a bundled WMM coefficient table in the first PR. Slice 1: hook design —
`Qibla.magnetic_direction(declination_deg)` pure function + `True North is default`
documentation + parameter threading (no I/O, no network, offline-first preserved).
Sign convention (verified, NOAA NCEI): declination positive east of true north,
`Magnetic = True − D_east` ("east is least"). Slice 2 (separate PR): optional
WMM/IGRF provider adapter (external data file or optional dependency) behind the
hook — and it must take **model version + epoch** (current: **WMM2025**, 5-year
release cycle; IGRF is the scientific retrospective/predictive alternative):
secular variation makes a timeless cached declination stale, so the hook API
carries `(model, epoch)` from day one.
Acceptance (slice 1): `magnetic = unwind(true − declination)` with sign convention
tested both hemispheres; docs show where a phone compass / WMM lookup plugs in,
with the epoch/version requirement stated.

#### 1.7 — Geodesy docs + error-budget note (TODO, docs-only PR)
Document when spherical vs. ellipsoidal matters for Qibla (typical few arcmin,
worst ~0.3° — **not** "sub-arcminute except near-antipode"), Kaaba 4-dp canonical
vs 7-dp display rounding (correction 3), and why Haversine alone is insufficient
as "high-precision" (spherical floor **~0.3–0.5%** distance error from flattening
`f ≈ 1/298`, not a hard 0.3%).
Acceptance: `docs/user/qibla.md` updated (including the 4-dp coordinate fix at
`:55`); no code change.

---

## Phase 2 — Solar Ephemeris & Extended Twilight (Prayer Times)

### Current state

| Milestone claim | State | Evidence |
|---|---|---|
| True solar position, EoT, declination (Meeus) | **PARTIAL** | `SolarCoordinates.py:17-41` + `Astronomical.py:6-100` implement truncated Meeus (mean longitude/anomaly, EoC 3-term, nutation 4-term, obliquity, sidereal time; all page-cited to Ch.22/25). Declination + RA at `SolarCoordinates.py:31-36` (Ch.25 p.165: `α=atan2(cos ε·sin λ, cos λ)`, `δ=asin(sin ε·sin λ)`). **No explicit `equation_of_time` symbol** — solar noon derived implicitly via Ch.15 transit interpolation (`SolarTime.py:24-39`, `PrayerTimes.py:154-159,212`). |
| Core times Fajr/Dhuhr/Asr/Maghrib/Isha (+Sunrise) | **DONE** | `PrayerTimes.py:255-408` (`_set_fajr/_set_sunrise/_set_dhuhr/_set_asr/_set_maghrib/_set_isha`); dispatch `time_for_prayer` at `:424-438`; `Prayer` enum `data/Prayer.py:4-18`. |
| Extended twilight / custom dawn-dusk angles (15°/18°/19°) | **PARTIAL** | Custom angles fully supported: `CalculationParameters.fajr_angle/isha_angle` (`CalculationParameters.py:34-35`), validated `[0,90]` (`:71-78`). Named presets cover 15/18/19.5 (see table). **No `Imsak` prayer/marker** — `Prayer.py` has only 6 + NONE; `PrayerAdjustments.py:1-44` has only 6 slots. "19°" alone is ambiguous (Egypt uses 19.5/17.5). |
| JAKIM/MUIS 20/18 | **PARTIAL** | `SINGAPORE` = 20/18 + dhuhr=1 (`MethodsParameters.py:41-45`) covers MUIS practice. **No `JAKIM`-named method**; Malaysia Takwim specifics (Imsak 10 min, Syuruk naming, 60-zone `zon` per-zone offsets, e-solat timetable deltas) unverified. |
| MWL 18/17 | **DONE** | `MethodsParameters.py:8-12` (dhuhr=1). |
| Egypt 19.5/17.5 | **DONE** | `MethodsParameters.py:13-17` (dhuhr=1). |
| ISNA 15/15 | **DONE** (as `NORTH_AMERICA`) | `MethodsParameters.py:34-38`; enum docstring `CalculationMethod.py:45-50` says "Referred to as the ISNA method". (Note: FCNA now recommends 15° US / 13° Canada — the 15/15 `NORTH_AMERICA` preset stays as the ISNA-legacy value.) |
| Asr shadow factors 1 (Shafi'i/Maliki/Hanbali) / 2 (Hanafi) | **DONE** | `data/ShadowLength.py:1-10` (SINGLE=1.0/DOUBLE=2.0), `calculation/Madhab.py:6-19`, `SolarTime.afternoon` (`SolarTime.py:82-88`), `PrayerTimes._set_asr` (`:310-341`, incl. Asr<Dhuhr clamp at `:336-341` and Asr>Maghrib clamp at `:215-219`). |
| Refraction offset −0.833° | **DONE** | `SolarTime.py:29` `solar_altitude = -50.0/60.0` for sunrise/sunset (34′ mean refraction + 16′ solar semi-diameter; Meeus Ch.15 standard `h₀=−0.8333°`). |
| Extra (not in milestone, already shipped) | **EXTRA / DONE** | `HighLatitudeRule` (MIDDLE/SEVENTH/TWILIGHT_ANGLE, `HighLatitudeRule.py:4-22`, `NightPortions.py:1-7`, `CalculationParameters.night_portions:84-94`); `PolarCircleRule` (NONE/NEAREST_LATITUDE default/NEAREST_DAY/MAKKAH, `PolarCircleRule.py:4-30`, resolver `PrayerTimes.py:224-253,25-85`); MSC seasonal twilight (`Twilight.py:24-73` — Shafaq-Ahmar/Abyad seasonal curves, 1/7-night above ~55°, verified against moonsighting.com); per-method minute offsets incl. DUBAI sunrise−3/dhuhr+3/asr+3/maghrib+3 and MSC dhuhr+5/maghrib+3 (`MethodsParameters.py:24-33`); Isha-interval mode 90 min for UMM_AL_QURA/QATAR (`PrayerTimes.py:351-408`, `MethodsParameters.py:23,40`); `PrayerAdjustments` user offsets (`PrayerTimes._rounded_minute:410-422`); 12-entry table incl. KARACHI 18/18, DUBAI 18.2, KUWAIT 18/17.5, QATAR 18+90min, UOIF 12/12 (`MethodsParameters.py:6-47`). |

### Corrections / clarifications to the milestone row

1. **ISNA vs NORTH_AMERICA naming**: code's `NORTH_AMERICA` *is* the ISNA 15/15
   preset — the milestone's "ISNA (15/15)" should be read as that row, not a missing
   method. Consider a follow-up alias, not a new computation.
2. **JAKIM ≠ SINGAPORE/MUIS astronomically identical, operationally distinct.**
   Core angles are the same 20/18 (PrayTimes, Fiqh Council, adhan ports all agree),
   so a `JAKIM` preset is *not* new astronomy — it is justified for
   presentation/operations: Malay naming (`Subuh/Syuruk/Zohor/Asar/Isyak`), the
   60-zone system (`WLY01`…), and official e-solat timetable deltas (published
   tables sometimes carry minute-level adjustments, e.g. the 2019 temporary +8 min
   Subuh, and Imsak rows that do not always equal exactly Fajr−10). Ship it as a
   separate preset with identical angles + distinct metadata, verified against
   Takwim Malaysia — do **not** claim a different twilight computation.
3. **"Custom dawn/dusk angles like 15°, 18°, 19°"** understates what exists: any
   angle in [0,90] is already accepted. The gap is *named markers* (Imsak, Syuruk/
   Ishraq, Dhuha) and *elevation/temperature-pressure* corrections, not angle plumbing.
4. **[FC 2026-10-02] Umm al-Qura Ramadan wording + Dubai offsets + Qatar conflict.**
   (a) The docstring prescribes "+30 min Isha during Ramadan"
   (`CalculationMethod.py:28-31`) but no code implements a Ramadan mode. The real
   practice is a **total** of 120 min in Ramadan vs 90 otherwise (PrayTimes, Fiqh
   Council, MasjidBox Ramadan-aware UQU) — specify `ishaInterval = 120` in Ramadan,
   not an additive "+30" setting. (b) The DUBAI `sunrise−3/dhuhr+3/asr+3/maghrib+3`
   offsets in `MethodsParameters.py:27` are **not canonical**: the Dubai preset is
   18.2°/18.2° per BatoulApps/AlAdhan ("not official… Batoul Apps research"); the
   minute offsets are app-level tuning with no IACAD/Awqaf source — flag for
   verification, do not present as authoritative. (c) QATAR 18°+90 min is the
   library-canonical preset, but Doha sources now cite Awqaf 18.5°+90 — record the
   conflict in docs when touching 2.1.
5. **Equation of time**: implicit Ch.15 transit is *related to*, not *equivalent to*,
   an EoT computation. EoT (`E = L₀ − 0.0057183° − α + Δψ·cos ε`, Ch.28 p.183) gives
   noon directly; Ch.15 interpolates 3-point RA/Dec to transit. They agree to seconds
   for the slow-moving Sun, but an explicit `equation_of_time` helper is still worth
   adding for testability against Ch.28 worked values — with tiered tolerances:
   ±10 s for the full-chain EoT value, ±30 s for coarse approximations, ±60 s for
   rise/set claims (low sun angle amplifies 0.01° to tens of seconds).
6. **[FC 2026-10-02] Dip coefficient.** Slice 2.6's `0.0347·√h` was wrong: the
   Nautical-Almanac/Bowditch standard is `dip = 1.76–1.77′·√h_m = 0.0293°·√h_m`
   (`h` in metres). `0.0347°` (2.08′/√m) is ~18% too large. Bennett/Saemundsson is
   an atmospheric-refraction-vs-altitude model, not dip — do not conflate.

### Slices (each = one PR)

#### 2.1 — Twilight preset audit + goldens (PARTIAL → DONE)
Lock one golden day per method (all 11 + NONE) with fajr/isha angles, dhuhr/method
offsets, and interval-vs-angle mode asserted. Pin the four milestone rows
(MWL/EGYPT/ISNA-via-NORTH_AMERICA/SINGAPORE-as-MUIS) explicitly. Record the Dubai
offset provenance gap and the Qatar 18-vs-18.5 conflict as doc notes, not blockers.
Acceptance: regression table in `tests/test_prayer_times.py`; any preset change fails loudly.

#### 2.2 — JAKIM preset + Takwim verification (TODO)
New `CalculationMethod.JAKIM` (20/18 base — identical angles to SINGAPORE by
design, distinct Malay naming + zone metadata; do **not** claim different
computation), verified against 2–3 Malaysian zones (Kuala Lumpur, Kota Kinabalu)
and documented delta vs SINGAPORE.
Acceptance: goldens + docs note stating what was checked (e-solat spot values + date).

#### 2.3 — Imsak marker (TODO)
`Imsak = Fajr − N min` (default 10, configurable; JAKIM convention — note published
Malaysian tables are *mostly* but not always exactly Fajr−10, so configurable is
load-bearing, not cosmetic). Touches `Prayer` enum, `PrayerAdjustments`,
`PrayerTimes`, `time_for_prayer`, CLI. This is the "extended twilight threshold
(Imsak pre-dawn withholding)" row made real.
Acceptance: `imsak = fajr − imsak_offset` (default 10 min) with minute-rounding order
specified (offset applied pre/post rounding — decide + test); NONE-method behavior defined.

#### 2.4 — Syuruk / Ishraq / Dhuha markers (TODO)
Sunrise-anchored derived markers. `Syuruk == sunrise` is naming for MY/SG users
(verified: MUIS/prayertime.sg `Syuruk` column = sunrise/end-of-Fajr). Ishraq at
+15–20 min post-sunrise is well-attested (Ibn Uthaymin 15 min). **Dhuha is an
interval (sunrise+~15 min until before Dhuhr), not a point** — the "+~28 min"
figure is a single Malaysian source (Syuruk+28), not universal fiqh; expose at most
a configurable `dhuha_offset` default and document the single-source status.
Pure derivation from computed sunrise — no new astronomy.
Acceptance: ordering invariant `fajr < sunrise <= syuruk <= ishraq_start <= dhuhr`
in tests (Dhuha asserted as window start, not a canonical point);
timezone-aware like `SunnahTimes.py:30-39`.

#### 2.5 — Explicit equation-of-time + declination helpers (TODO, small)
Expose `equation_of_time(jd)` / `solar_declination(jd)` wrappers over existing
`SolarCoordinates` internals (no algorithm change; Ch.28 formulation), tested
against Meeus Ch.28 worked values.
Acceptance: EoT within ±10 s of Meeus example for the full chain (±30 s if a
coarse path is exposed); transit times unchanged (characterization test).

#### 2.6 — Observer elevation correction (TODO)
Add optional `elevation_m` (default 0 = current behavior): dip-of-horizon correction
to sunrise/sunset/Maghrib (`h₀ = −0.833° − 0.0293°·√h_m`, `h_m` in metres —
**not** 0.0347; valid for eye heights ~0–tens of metres). Thread through
`Coordinates` or `CalculationParameters` (decide once), default-off so all goldens hold.
Acceptance: sea-level goldens unchanged; e.g. 1000 m shifts sunrise/sunset by ~±3 min
(asserted range, not exact).

#### 2.7 — Umm al-Qura Ramadan mode (TODO, tiny)
Implement the documented Ramadan behavior as an explicit opt-in flag
(`ishaInterval = 120` total in Ramadan vs 90 otherwise — **not** an additive +30),
or remove the docstring claim. Decide: `is_ramadan: bool` on parameters vs.
caller-side `PrayerAdjustments(isha=30)`.
Acceptance: docstring and behavior agree; non-Ramadan path unchanged.

#### 2.8 — Twilight docs (TODO, docs-only)
Document angle-vs-interval Isha (`MethodsParameters.py:23,40` 90-min mode), DUBAI/MSC
method offsets (with Dubai-offset provenance caveat), MSC seasonal-twilight +
lat≥55 rules (`PrayerTimes.py:262-276,374-391`), and
`HighLatitudeRule`/`PolarCircleRule` interaction. These exist but are undiscoverable.

---

## Phase 3 — Night Divisions & Temporal Markers

### Current state

| Milestone claim | State | Evidence |
|---|---|---|
| Last third / middle / halves of night (Thuluth al-Layl, Tahajjud) | **PARTIAL** | `SunnahTimes.py:13-17,30-39`: `middle_of_the_night` (Maghrib→next-day-Fajr ÷ 2) and `last_third_of_the_night` (Maghrib + ⅔ night). UTC-duration math with DST-safe `astimezone` (`:30-36` — the correct best practice: compute durations in UTC, convert for output); recomputes tomorrow's Fajr (`:20-25`). |
| Fractional splits 1/2, 1/3, 2/3 | **PARTIAL** | 1/2 and 2/3 exist as above. **No `first_third` (1/3 offset), no generic `night_fraction(f)` API.** `NightPortions` (`data/NightPortions.py:1-7`) is unrelated (high-latitude Fajr/Isha caps). |

### Corrections / clarifications

1. **Interval definition**: the code uses Maghrib → *next-day* Fajr (not "Sunset → Fajr"
   same-day). The milestone's "interval between Sunset and Fajr" should be amended to
   "Maghrib to next-day Fajr" — same instants in practice (Maghrib = sunset + offsets),
   but the next-day rollover and the offset-inclusion choice must be stated.
2. **"Halves" (plural)** is ambiguous: there is one middle marker, not two half-markers.
   If "halves" means first-half/second-half windows, that is a Tahajjud-window feature,
   not a marker.
3. **School sensitivity**: some authorities anchor the night at Isha (not Maghrib) or
   at astronomical sunset (ignoring Maghrib offsets). The generic-fraction API should
   take an explicit anchor pair rather than hardcoding.

### Slices

#### 3.1 — `first_third_of_the_night` (TODO, tiny)
Mirror `last_third_of_the_night`: Maghrib + ⅓ night. Same UTC-duration pattern
(`SunnahTimes.py:30-39`).
Acceptance: `first_third < middle < last_third`, all within (maghrib, fajr_next);
goldens in `tests/test_sunnah_times.py`.

#### 3.2 — Generic `night_fraction(f)` + anchor options (TODO)
`SunnahTimes.night_fraction(f: float)` with `0 < f < 1` (+ enum or explicit
`start/end` datetimes for Isha-anchored and sunset-anchored variants). Middle/last/
first-third become thin wrappers.
Acceptance: wrappers equal `night_fraction(1/2|1/3|2/3)` to the second; invalid `f`
raises `ValidationError` (follow `Coordinates.py` precedent).

#### 3.3 — Tahajjud / Qiyam window semantics (TODO, small)
Document + expose the *window* (last-third → Fajr) as a first-class concept
(`tahajjud_window: tuple[datetime, datetime]`), rather than leaving callers to
subtract. No new math. Spring-forward precedent exists
(`tests/test_sunnah_times.py`, `2015-03-07/08 America/New_York`); fall-back `fold`
handling (PEP 495) belongs to slice 6.3 — reuse its decision here.
Acceptance: window endpoints equal existing markers; DST-transition-night test
for both spring-forward and fall-back.

#### 3.4 — Night-division docs (TODO, docs-only)
State the Maghrib→next-day-Fajr definition, offset inclusion, rounding order
(`rounded_minute` before `astimezone`, `SunnahTimes.py:34-39`), and the Isha-anchor
alternative. One page under `docs/user/`.

---

## Phase 4 — Advanced Hijri Calendar & Moon Sighting

### Current state

| Milestone claim | State | Evidence |
|---|---|---|
| Tabular / visibility-based calendar generation | **TODO** | No `Hijri*`/`Calendar*`/`Converter*` module in `src/`. |
| Yallop criterion (1997), zones A–F | **TODO** | Zero hits for `yallop|Yallop|crescent|hilal` in `src/`. |
| Odeh criterion (2004) | **TODO** | Zero hits for `odeh|Odeh` in `src/`. |
| MABIMS / Neo-MABIMS (alt ≥ 3°, elongation ≥ 6.4°) **[FC 2026-10-02: was 4° — wrong]** | **TODO** | Zero hits for `mabims|MABIMS` in `src/`. Only lunar-related code is `mean_lunar_longitude` + `ascending_lunar_node_longitude` (`Astronomical.py:15-30`), used **solely** as solar nutation inputs (`SolarCoordinates.py:21-22`) — not a Moon position. |
| Lunar ephemeris (dependency of all above) | **TODO** | No Moon RA/Dec, no elongation, no phase/illumination anywhere in `src/`. |

### Corrections / clarifications

1. **Yallop zones A–F are an *output* classification**, computed from the `q`-value —
   but `q` is **not** `f(ARCV, DAZ, width)` as three independents (prior draft's
   phrasing). Per Yallop §2–3 (NAO Technical Note No.69 — the correct bib, not
   "UKHO Technical Report"): `ARCL` = geocentric elongation (Sun-centre–Moon-centre),
   `ARCV` = *geocentric* altitude difference ignoring refraction, `DAZ` = azimuth
   difference, with `cos ARCL = cos ARCV · cos DAZ`. The criterion recasts to an
   `ARCV`-vs-width limit curve (eq. 3.6, Indian-method fit); final `q` uses
   *topocentric* width `W′ = SD′·(1 − cos ARCL)` with `SD = 0.27245·π`, evaluated at
   **best time `Tb = Ts + 4/9·Lag`**. DAZ enters only via `W(ARCL(ARCV,DAZ))`, and
   ARCV stays geocentric in Yallop — topocentric ARCV is Odeh's innovation. Calibrated
   on 295 sightings 1859–1996: **A `q>+0.216`** easily visible naked eye;
   **B `−0.014<q<+0.216`** visible under perfect conditions;
   **C `−0.160<q<−0.014`** may need optical aid to find, then naked eye;
   **D `−0.232<q<−0.160`** optical aid only; **E `−0.293<q<−0.232`** below normal
   telescope limit; **F `q<−0.293`** not visible (Danjon limit). Implement `q` first,
   zones second.
2. **[FC 2026-10-02] Neo-MABIMS is alt ≥ 3° (not 4°) + elongation ≥ 6.4°, at local
   sunset on the 29th — and so is the MILESTONES.md row wrong, not just this doc.**
   History: Istanbul 26–29 Nov 1978 resolved 5°/8° (+ Malaysian delegate's 8 h age
   proposal); Malaysia interim 1983 used 5.5°/7.5°/8 h; the *modified* Imkanur Rukyah
   (`alt ≥ 2° AND elong ≥ 3°`, **OR** `age ≥ 8 h at moonset`) was agreed at Labuan
   1 Jun 1992 (for Ramadan/Syawwal/Zulhijjah; all months MY 1995/96, ID 1998) — not
   "1978". The *new* Imkanur Rukyat (KBIR: `alt ≥ 3° AND elong ≥ 6.4°` at sunset,
   **age condition dropped**) was recommended at the 2–4 Aug 2016 MABIMS
   muzakarah, formally adopted 2021, effective Muharram 1443H / 2021 (MY) and the
   2022 calendar (ID). No official source supports 4°. Fix `MILESTONES.md` too, and
   keep the old preset as a legacy migration path.
3. **Odeh's `V`** derives from an ARCV-minus-limit curve in the same polynomial
   family as Yallop eq. 3.6 but with the intercept lowered 11.8371 → 7.1651:
   `V = ARCV − (−0.1018·W³ + 0.7319·W² − 6.3226·W + 7.1651)` (airless *topocentric*
   ARCV, topocentric `W` in arcmin; 737 records). Correct bib: M.Sh. Odeh,
   *New Criterion for Lunar Crescent Visibility*, **Experimental Astronomy
   18:39–64** (presented 2004, print often cited 2005/06; AUASS/ICOP — not
   "ICAS/JAS"). Classes: **A `V≥5.65`** naked eye; **B `2≤V<5.65`** optical aid,
   possibly naked eye; **C `−0.96≤V<2`** optical aid only; **D `V<−0.96`**
   invisible even with optical aid — plus **`ARCL<6.4° → D`** explicitly. The
   Danjon limit (~7°, variants 7–8°; Schaefer 1991 confirms 7°, Sultan 2007: 7.5°,
   Odeh's dataset finds 6.4° with optical aid) emerges from `W→0` in Yallop's Zone F
   rather than a separate cutoff.
4. **Lunar accuracy tier must be chosen explicitly**: Meeus low-precision Moon
   (**Ch.47 only** — prior draft's "Ch.45–47" is wrong; 45/46 are Saturn; Tables
   47.A–B pp.339–341), worked example **Ex.47.a: 1992-04-12 0h TD (= TT, not UTC —
   secondaries that write "UTC" are wrong), JDE 2448724.5 → λ=133.167265°,
   β=−3.229126°, Δ=368409.7 km**, ~10″–1′ — sufficient for crescent prediction)
   vs. full ELP-2000. Start with Meeus low-precision; document the error budget
   vs. Yallop/Odeh sensitivity (Yallop zone widths are ~0.05–0.2 in `q`; arcminute
   lunar error is well inside a zone except exactly on a boundary — state boundary
   behavior explicitly).
5. **ΔT: get the numbers and the framing right.** Today `TT − UTC = 69.184 s`
   exactly (TAI−UTC=37 s since 2017, +32.184 s TT−TAI), ±0.9 s UT1 band ⇒ ΔT ≈
   68.3–70.1 s in 2025 — the "69–70 s" range holds. Use Espenak/Meeus polynomials
   by range (1986–2005 5th-degree; 2005–2050 `ΔT = 62.92+0.32217·t+0.005589·t²`,
   `t = y−2000`; Morrison/Stephenson spline 700 BCE–1600 CE outside), and prefer
   IERS observed values for modern dates (polynomial drift reached ~5 s by 2024).
   Framing correction: 69 s = 17.5′ hour-angle shift ≈ 1.15 min systematic — small
   but *not* negligible for prayer times (apply it; minute-rounding + angle-convention
   scatter merely dominates it). For crescents the elongation error is only ~35″
   (Moon ~0.5″/s vs Sun) ≪ Danjon 7° — **not** load-bearing for the visibility
   judgment itself; load-bearing for absolute times (conjunction/moonset lag shift
   ~70 s) and eclipse longitude (~17.5′ ≈ 30 km). State which side of that line each
   slice lives on.
6. **Topocentric is non-negotiable, and large.** Lunar horizontal parallax reaches
   ~54′–61.4′ (~1°, the largest of any body); geocentric vs topocentric altitude
   differs by up to ~1° before refraction. Crescent geometry must be topocentric at
   best time — geocentric elongation alone is a category error at MABIMS thresholds.

### Slices (dependency-ordered; each = one PR)

#### 4.1 — Lunar position module (TODO, foundation)
New `astronomy/LunarCoordinates.py`: Meeus low-precision geocentric Moon RA/Dec +
distance (**Ch.47**, Ex.47.a goldens above: JDE 2448724.5 → λ, β, Δ quoted in
correction 4).
Acceptance: RA/Dec within documented tolerance of Ex.47.a; no prayer-time
regression (new module, no callers yet).

#### 4.2 — ΔT provider (TODO, small, before any visibility math)
`astronomy/DeltaT.py`: Espenak-range polynomial ΔT(T) + explicit override parameter;
validity ranges documented per correction 5 (Morrison/Stephenson historical,
IERS-observed preference modern). Wire into lunar/solar JD→TT paths used by Phase 4
(leave prayer path default behavior unchanged or explicitly migrated — note the
~1 min systematic so the migration decision is recorded).
Acceptance: ΔT(2025) ≈ 68.3–70.1 s asserted as range; override respected.

#### 4.3 — Sun–Moon geometry at sunset (TODO)
Topocentric elongation (ARCL), arc of vision (ARCV — state geocentric vs topocentric
per API name; Yallop takes geocentric, Odeh airless topocentric), relative azimuth
(DAZ), crescent width `W = SD·(1 − cos ARCL)` / illumination `I = (1 − cos ARCL)/2`,
lag time, moon age, illumination — evaluated at local sunset (and best time
`Tb = Ts + 4/9·Lag` for Yallop) from existing `SolarTime` + new `LunarCoordinates`.
Pure functions, fully unit-testable.
Acceptance: goldens for 2–3 known crescents (e.g. a confirmed + a negative sighting);
geocentric vs. topocentric distinguished in API names.

#### 4.4 — Yallop criterion (TODO)
`q`-value + zones A–F with the numeric boundaries in correction 1, per Yallop 1997
(NAO TN No.69).
Acceptance: published Yallop test cases reproduced (zone boundaries); each zone maps
to the milestone's A–F labels.

#### 4.5 — Odeh criterion (TODO)
`V`-value + Odeh classes with the numeric boundaries in correction 3, per Odeh
2004/Exp.Astron. 18 (including the `ARCL<6.4° → D` rule).
Acceptance: Odeh reference cases; cross-check Yallop vs. Odeh agreement matrix on a
small date/location grid (disagreements documented, not forced to agree).

#### 4.6 — MABIMS old + Neo presets (TODO)
`MABIMS_1992` (`2°/3°`-or-`8 h`, Labuan agreement — **not** "1978") and
`NEO_MABIMS_2021` (**3°/6.4°** at sunset, age dropped — **not** 4°) as thin
predicates over 4.3 outputs. This is the Malaysia/Indonesia/Brunei/Singapore
Takwim hook for Phase 5.
Acceptance: both presets evaluated on same sunset instants; migration note (which
historical dates flip 1992→2021 rule) in docs; `MILESTONES.md` 4° value fixed.

#### 4.7 — Visibility-map export (TODO, optional/last)
Grid evaluation helper (lat/lon × date → Yallop/Odeh/MABIMS class) emitting GeoJSON/
CSV for `docs_site/` visualization. No new science — I/O over 4.3–4.6.
Acceptance: script + sample output for one Ramadan/Syawwal eve; performance note
(pure-Python grid cost, caching strategy).

---

## Phase 5 — Unified Hijri Converter & Override Layer

### Current state

| Milestone claim | State | Evidence |
|---|---|---|
| Sunset-aligned transitions (prayer↔calendar bridge) | **TODO** | No Hijri date type; `PrayerTimes` is Gregorian-date-in/UTC-datetime-out only. `SunnahTimes` rolls to next-day Fajr but has no calendar notion. |
| Algorithmic (Kuwaiti/tabular) vs. observational flexibility | **TODO** | "Kuwaiti" appears nowhere in `src/`. `CalculationMethod.UMM_AL_QURA` (`CalculationMethod.py:26-31`) is a *prayer* preset (Fajr 18.5 + 90-min Isha), not a calendar. |
| JSON delta offsets (`{"YYYY-MM": ±1}`) | **TODO** | Only prayer-minute offsets exist (`PrayerAdjustments`, applied in `PrayerTimes._rounded_minute:410-422`). No date-correction store. |
| Regional Takwim (Umm al-Qura calendar, SE-Asian standards) | **TODO** | No calendar code of any kind. |

### Corrections / clarifications

1. **[FC 2026-10-02] "Kuwaiti algorithm" is standard tabular Type IIa, not distinct
   astronomy.** The tabular Islamic calendar is: epoch 1 Muharram 1 AH = Fri 16 Jul
   622 Julian (= 19 Jul 622 Gregorian proleptic), JD 1948439.5 (noon epoch) + 30-year
   leap cycle (Type IIa: years 2,5,7,10,13,16,18,21,24,26,29 have 355 days — the
   al-Fazari/al-Khwarizmi/al-Battani pattern) + bidirectional JD↔Hijri arithmetic.
   "Kuwaiti" (Microsoft's label, after claimed statistical analysis of Kuwaiti
   historical data) computes **identical** results to Type IIa; its only real
   difference is the adjustable `HijriAdjustment` ±2-day nudge (Windows/.NET
   `HijriCalendar`, SQL Server) toward observed dates. Name the variant, cite van
   Gent, and note sibling patterns exist (Kushyar/Ulugh Beg `…15…`; Fatimid/Tayyibi
   `2,5,8,10,13,16,19,21,24,27,29`; Habash/al-Biruni; 8-yr Ottoman/SE-Asia cycle).
   Tabular vs observed routinely differs ±1–2 days — the converter must never
   present tabular output as a sighting.
2. **[FC 2026-10-02] Umm al-Qura *calendar* ≠ Umm al-Qura *prayer preset*, and the
   current month rule has no age/elongation thresholds.** Versioned rules (van Gent
   / KACST): pre-1392H uncertain; 1392–1419H: conjunction <3 h after Saudi midnight
   ⇒ month starts previous sunset; 1420–1422H: moonset-after-sunset at Makkah (Great
   Mosque); **since 1423H (15 Mar 2002): on the 29th, geocentric conjunction before
   Makkah sunset AND moonset after Makkah sunset ⇒ next day is the 1st, else 30 days**
   (anomalous pre-conjunction starts in Rajab 1421 / Shaban 1422 forced the 1423
   fix; no 1438 month-rule change). Do not implement "moon age/elongation
   conditions" — that describes *other* calendars' rules, not UQU. Name the module
   `UmmAlQuraCalendar` to force the distinction from `CalculationMethod.UMM_AL_QURA`
   (Fajr 18.5° + 90/120-min Isha).
3. **Sunset transition needs a flag, not magic.** `HijriDate.from_gregorian(dt,
   change_at_sunset=True/False)` — with `True`, post-Maghrib evening belongs to the
   next Hijri day, computed from that location's actual Maghrib (bridging
   PrayerTimes↔calendar as the milestone asks).

### Slices

#### 5.1 — `HijriDate` value type + tabular (Kuwaiti) conversion (TODO, foundation)
Immutable `HijriDate(y,m,d)` + both directions Gregorian↔Hijri via tabular
arithmetic (Type IIa 30-year cycle, leap set above; document the "Kuwaiti" =
Type IIa + `HijriAdjustment` equivalence), validated against known anchors. Anchor
note: **1 Ramadan 1446 = Sat 2025-03-01 is an *observed* Saudi date** (sighting Fri
evening 28 Feb 2025, SPA; joined by UAE/Qatar/Egypt/ID/MY/SG; except Morocco,
IN/PK/BD on 2 Mar) — tabular happens to agree that month, but tabular vs observed
routinely differs ±1–2 d, so the test asserts the *tabular* value with documented
variance, never "tabular proves the sighting".
Acceptance: round-trip property test (Gregorian→Hijri→Gregorian) over 1900–2100;
month-length 29/30 respected; out-of-range raises `ValidationError`.

#### 5.2 — Umm al-Qura calendar (TODO)
Observational-rule calendar per the **post-1423H rule text** in correction 2
(conjunction-before-sunset + moonset-after-sunset at Makkah; cite adopted version
and the 1392/1420/1423 history), built on Phase 4.3 sunset geometry at Makkah.
Distinct module from prayer preset; name it `UmmAlQuraCalendar` to force the distinction.
Acceptance: 12-month spot check for 2 recent Hijri years vs. published UQU dates
(deltas listed, not hidden).

#### 5.3 — MABIMS Takwim calendar (TODO)
SE-Asian Hijri calendar applying Neo-MABIMS 3°/6.4° (Phase 4.6) at regional
reference points + country zone handling. This is the JAKIM-adjacent deliverable
the milestone's "regional Southeast Asian standards" points at.
Acceptance: Ramadan/Syawal 1–2 years vs. Malaysian/Indonesian announcements (deltas listed).

#### 5.4 — Sunset-transition bridge (TODO, small)
`change_at_sunset` flag + `gregorian_to_hijri(dt, coordinates, params)` using that
day's computed Maghrib. Explicitly tested around Maghrib ± 5 min.
Acceptance: pre/post-Maghrib datetimes on the same civil date map to successive Hijri
days when flag is on, same day when off.

#### 5.5 — JSON delta-offset store (TODO)
`{"YYYY-MM": ±1}` regional correction file (schema + loader + precedence:
offsets > computed), per-region files (e.g. `takwim-my.json`), CLI flag to point at a file.
Acceptance: offset shifts `HijriDate` by exactly ±1 day for covered months; unknown keys rejected with `ConfigurationError`.

#### 5.6 — Converter CLI + docs (TODO)
`python -m alfalak hijri --date --location --calendar {tabular,uqu,mabims} [--sunset-transition] [--offsets file]`.
Acceptance: man-page-level `--help`; current prayer CLI output unchanged
(`tests/test_cli.py` still green).

---

## Phase 6 — Performance, Validation & Ecosystem

### Current state

| Milestone claim | State | Evidence |
|---|---|---|
| Cross-library benchmark vs. Adhan JS/Go/Swift | **TODO** | No `test_benchmark*`/`test_cross*` in `tests/` (20 test modules + `support.py`, none matching). Existing suites are internal goldens/invariants: `test_prayer_times.py` (Raleigh goldens `04:42AM…`, second-locked UTC `08:42:00…` at `:251-264`), `test_validation.py`, `test_parameterized_sweep.py` (SEED 20260929, ≤200 cases), `test_blackbox_sweep.py` (public-seam only). |
| Historical/political tz robustness + DST edges | **PARTIAL** | `ZoneInfo` threading exists (`PrayerTimes.py:5,102,136,222,440-447`, `SunnahTimes.py:30-36` UTC-duration DST fix) with `America/New_York, Europe/Oslo, Europe/London` tests incl. spring-forward (`test_sunnah_times.py`). **Missing**: fall-back ambiguity (`fold`, PEP 495), pre-1970/historical offset changes, CLI `--timezone` (CLI is UTC-only, `__main__.py:1-53`), tzdata-on-Windows strategy. |
| zoneinfo integration | **PARTIAL** (DONE for library, TODO for CLI/packaging) | Library accepts `ZoneInfo`; CLI does not expose it; no tzdata dependency strategy (Python docs: Windows has no system IANA DB — the PyPI `tzdata` package is the fallback; this gap is real and widely reported). |
| ≤1 s precision tolerance | **TODO** (and currently unachievable as stated — see correction 2) | Public API minute-rounds (`CalendarUtil.rounded_minute:1-17`); tests assert minute goldens + a second-locked characterization, qibla `abs=1e-2°`, astronomical `1e-4…1e-11`, calendrical `1e-5/1e-6` (`tests/`). A ≤1 s bar requires an unrounded/second-precision mode that does not exist. |

### Corrections / clarifications

1. **[FC 2026-10-02] Adhan-port agreement is necessary but weak validation — and get
   the lineage right.** Cross-port tests catch porting bugs, not algorithm bugs: all
   ports share the same truncated-Meeus core. Origin is BatoulApps **adhan-java**
   (Java/Android); Kotlin/Swift/JS are official Batoul ports — the "original
   adhan-kotlin" phrasing in `Qibla.py:11`/`SunnahTimes.py:9` names this repo's
   *direct* parent, not the lineage root. `adhanpy` (alphahm) is a **third-party**
   Python port ("a port of batoulapps/adhan-java… from Java to Python"), not a
   Batoul/Batts artifact; there is no official `batoulapps/adhan-go`. Independent
   references (Meeus worked examples, USNO, official Takwim spot values) must carry
   equal weight to cross-port deltas.
2. **≤1 s tolerance contradicts minute rounding *and* overclaims physics.** Adopt a
   two-tier policy: (a) *internal* (unrounded `SolarTime` interpolation) ≤1 s vs.
   reference — framed as a **port-fidelity** assertion, not physical accuracy (the
   truncated solar theory is ~1′-class ≈ 4 s in RA before refraction, and operational
   sunrise/sunset carry minutes of refraction/model uncertainty; "all programs
   assume nominal 0.567°" per Fiqh Council/Saifee refs); (b) *public* (rounded)
   exact-minute agreement. Benchmark harness must compare tier (a).
3. **zoneinfo ≠ historical robustness.** IANA pre-1970 data is patchy *by design*
   (theory.html: railway/church/political disagreements, sub-second specs
   unrepresentable — e.g. France 1891–1911). One pre-1980s test case gives false
   confidence and system-vs-PyPI `tzdata` skew is already demonstrated (Amsterdam
   1923: 1172 s vs 0.0 s across hosts). Pin the `tzdata` version and test a matrix
   of *modern* political/DST rule changes plus `fold`/nonexistent-time policy —
   not one old date. Southern-hemisphere Ramadan is **not** a library risk class
   (solar formulas are declination-symmetric; fasting-hours press is just inverted
   seasons) — the real risk class is high latitude (|lat| ≳ 48–66°: polar
   day/night, indeterminable Fajr/Isha). Keep a Sydney case as smoke, but spend the
   matrix budget on high-latitude + IANA-transition cases.

### Slices

#### 6.1 — Cross-port benchmark harness (TODO)
`tests/benchmark/` (or `scripts/`) comparing unrounded outputs vs. Adhan reference
implementations (pin versions + commit SHAs; note shared lineage per correction 1 —
port deltas assert fidelity, Meeus/USNO/Takwim assert truth) on a fixed city×date
grid; stores deltas, fails over threshold. Tier-(a) comparison per correction 2.
Acceptance: harness runs in CI; baseline report committed under `docs/development/baseline/`
(next to `2026-09-24-baseline.md`); failures print max-delta case.

#### 6.2 — Independent-reference goldens (TODO)
Meeus worked-example assertions (solar longitude Ex.25.a p.165: JDE 2448908.5 →
α=13h13m31.4s, δ=−7°47′06″; transit) + USNO spot checks + 2–3 Takwim/JAKIM
published times (documented as spot values with date + source URL).
Acceptance: each golden cites source page/URL + edition; tolerances per-correction-2 tiers.

#### 6.3 — Timezone robustness matrix (PARTIAL → DONE)
Fall-back `fold` night (e.g. America/New_York 2015-11-01, PEP 495 both folds) for
SunnahTimes; high-latitude cases (the actual risk class, e.g. Oslo winter already
partially covered — extend toward 60°+ polar rules); pinned-`tzdata` modern
political-change cases; nonexistent-local-time policy documented. Extends existing
spring-forward test. Southern-hemisphere ordinary case (e.g. Sydney) kept as smoke
only — not presented as the hard case.
Acceptance: matrix test file; each case states expected behavior (not just "no crash").

#### 6.4 — Second-precision mode (TODO, API decision)
Expose unrounded times (flag or accessor) so the ≤1 s *port-fidelity* bar is
measurable; decide rounding order canonically (`rounded_minute` currently
post-offset, `PrayerTimes._rounded_minute:410-422`, `SunnahTimes.py:34-39`).
Default output unchanged.
Acceptance: RFC-style decision in plan + `time_for_prayer`-compatible accessor + tests.

#### 6.5 — CLI timezone + packaging (PARTIAL → DONE)
`--timezone ZoneInfo` for `python -m alfalak` (`__main__.py`), `tzdata` guidance /
dependency for Windows, `tests/test_cli.py` extension.
Acceptance: CLI prints local ISO-8601 with offset; UTC default unchanged.

#### 6.6 — Performance + fuzz (TODO)
Cache `SolarCoordinates` per (JD) within a `PrayerTimes` build (today computes
prev/day/next redundantly across tomorrow's `SolarTime` + `SunnahTimes` rebuild at
`SunnahTimes.py:20-25` — plausible hygiene micro-opt at ~µs per eval of a few
sin/cos/atan2; profile before claiming any % target); property fuzz (random
lat/lon/date ordering invariants: `fajr ≤ sunrise ≤ dhuhr ≤ asr ≤ maghrib ≤ isha`
— gated on non-polar schedule-defined days, since NaN/non-ordering is *expected*
outside polar rules per PrayTimes higher-latitude docs — no NaN inside).
Acceptance: benchmark note (before/after ms on reference grid); fuzz runs N=2000 in CI
without new deps (stdlib `random` with fixed seed, following `test_parameterized_sweep.py` precedent).

---

## Suggested PR order (cross-phase)

1. 1.3, 2.1 (harden what exists; no API change).
2. 1.1, 1.2, 6.2 (golden locks; independent references early).
3. 2.3, 3.1–3.2 (derived markers; small, high user value — Imsak + first-third).
4. 2.5, 2.6, 6.4 (precision story: EoT helpers → elevation → second-precision mode).
5. 1.4, 1.5, 1.6 (geodesy expansion; needs constants-module decision from 1.3).
6. 4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 4.6 → 4.7 (strict chain; do not parallelize).
7. 5.1 → 5.2 → 5.3 → 5.4 → 5.5 → 5.6 (needs 4.3+; 5.1 tabular can start in parallel with 4.x).
8. 2.2, 2.7, 5.3 (Malaysia track: JAKIM preset → Ramadan note → MABIMS Takwim).
9. 6.1, 6.3, 6.5, 6.6 (ecosystem last; 6.1 needs 6.4's tier decision).

Also fix `MILESTONES.md` Phase-4 row: Neo-MABIMS "≥ 4°" → "≥ 3°" (Phase 4 correction 2).

## Test strategy (applies to all slices)

- Golden tests cite primary sources (Meeus page + edition, Yallop/Odeh paper table, Takwim URL+date).
- Ordering/round-trip invariants accompany every new marker or converter (ordering gated on schedule-defined days; polar behavior asserted separately).
- New public API is exported via `alfalak/__init__.py` (`__all__`, currently 15 names, `:19-35`) and covered by `tests/test_public_api.py` + `test_blackbox_sweep.py`.
- Polar/DST edge cases reuse the `ZoneInfo America/New_York` spring-forward precedent (`tests/test_sunnah_times.py`) plus the new fall-back case (6.3).
- Pin `tzdata` version for the timezone matrix; record IERS-vs-polynomial ΔT choice wherever crescent goldens depend on it.

## Key references (fact-check backbone, 2026-10-02)

- Meeus, *Astronomical Algorithms*, 2nd ed. (Willmann-Bell, 1998): Ch.3/7/12/15/22/25/28/47.
- Yallop, *A Method for Predicting the First Sighting of the New Crescent Moon*, NAO Technical Note No.69 (1997).
- Odeh, *New Criterion for Lunar Crescent Visibility*, Experimental Astronomy 18:39–64 (presented 2004).
- Vincenty, *Direct and Inverse Solutions of Geodesics on the Ellipsoid* (1975); Karney, *Algorithms for Geodesics*, J. Geodesy 87:43–55 (2013) + GeographicLib.
- NGA WGS-84 manual (a, 1/f defining); NOAA/NCEI World Magnetic Model 2025 (5-year cycle).
- praytimes.org (PrayTimes Hamid; UQU 90/120-min Ramadan; high-latitude rules); Fiqh Council NA calculation notes; moonsighting.com (MSC seasonal method); BatoulApps Adhan ports (adhan-java origin; Kotlin/Swift/JS official; adhanpy third-party).
- MABIMS: Istanbul 1978 → Labuan 1992 (2°/3°-or-8h) → KBIR 2016/2021 (3°/6.4°); Umm al-Qura calendar rule history (van Gent/KACST: 1392/1420/1423H versions).
- IANA time-zone theory.html (pre-1970 limits); Python `zoneinfo` + PyPI `tzdata` docs; PEP 495 (`fold`).
