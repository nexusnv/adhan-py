# Exception Hierarchy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace builtin failure types with a dedicated `AlFalakError` tree (clean break, version 2.0.0) per `docs/superpowers/specs/2026-09-28-exception-hierarchy-design.md`.

**Architecture:** One new dependency-free module (`src/alfalak/exceptions.py`); mechanical type swaps at 15 raise sites with messages unchanged; tests updated to the new types; docs + version signal.

**Tech Stack:** Python 3.11+, pytest 9, mypy `disallow_untyped_defs`, ruff (F, E4/E7/E9), black.

---

**Prerequisite (run once):**

```bash
git checkout dev && git pull origin dev && git checkout -b feat/exception-hierarchy
```

Venv for all runs below: `/tmp/opencode/adhan-bump/bin/python` (has the pinned toolchain). Full-suite command used throughout:

```bash
/tmp/opencode/adhan-bump/bin/python -m pytest -q -p no:cacheprovider --no-cov
```

## File structure

- Create `src/alfalak/exceptions.py` — 4 classes, no imports.
- Modify `src/alfalak/PrayerTimes.py` — import + 6 swaps + 1 comment.
- Modify `src/alfalak/calculation/CalculationParameters.py` — import + 4 swaps.
- Modify `src/alfalak/calculation/Madhab.py` — import + 1 swap.
- Modify `src/alfalak/data/Coordinates.py` — import + 2 swaps.
- Modify `src/alfalak/__init__.py` — export 4 names + `__all__`.
- Modify `pyproject.toml` — version `1.0.5` → `2.0.0`.
- Tests: create `tests/test_exceptions.py`; update `tests/test_PrayerTimes.py`, `tests/test_PolarCircle.py`, `tests/test_CalculationParameters.py`, `tests/test_Madhab.py`, `tests/test_validation.py`, `tests/test_public_api.py`.
- Docs: `docs/api.md` (append Errors section), `docs/migration.md` (append breaking section), `CHANGES.md` (`2.0.0` entry).

### Task 1: exceptions module + its tests

**Files:**
- Create: `src/alfalak/exceptions.py`
- Create: `tests/test_exceptions.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from alfalak.exceptions import (
    AlFalakError,
    AstronomicalError,
    ConfigurationError,
    ValidationError,
)


def test_hierarchy():
    assert issubclass(AstronomicalError, AlFalakError)
    assert issubclass(ConfigurationError, AlFalakError)
    assert issubclass(ValidationError, AlFalakError)
    assert not issubclass(AlFalakError, RuntimeError)
    assert not issubclass(AlFalakError, ValueError)


def test_catch_all_base():
    with pytest.raises(AlFalakError):
        raise AstronomicalError("polar day")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/tmp/opencode/adhan-bump/bin/python -m pytest tests/test_exceptions.py -q -p no:cacheprovider --no-cov`
Expected: FAIL with `ModuleNotFoundError: No module named 'alfalak.exceptions'`

- [ ] **Step 3: Write minimal implementation**

```python
class AlFalakError(Exception):
    """Base class for all al-falak errors."""


class AstronomicalError(AlFalakError):
    """The sun position needed for a marker is undefined
    (polar day/night, undefined Asr)."""


class ConfigurationError(AlFalakError):
    """Invalid setup (method, madhab, polar rule, prayer,
    high-latitude rule, method-vs-parameters exclusivity)."""


class ValidationError(AlFalakError):
    """Out-of-range value (coordinates, angles, intervals)."""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `/tmp/opencode/adhan-bump/bin/python -m pytest tests/test_exceptions.py -q -p no:cacheprovider --no-cov`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/alfalak/exceptions.py tests/test_exceptions.py
git commit -m "feat: add AlFalakError hierarchy (issue #7)"
```

### Task 2: Migrate PrayerTimes raise sites

**Files:**
- Modify: `src/alfalak/PrayerTimes.py`
- Modify: `tests/test_PrayerTimes.py`
- Modify: `tests/test_PolarCircle.py`

Exact swaps in `src/alfalak/PrayerTimes.py` (messages byte-identical):

1. Add import after the `PrayerAdjustments` import line:
```python
from alfalak.exceptions import AstronomicalError, ConfigurationError
```
2. `raise RuntimeError(` (polar message, ~line 169) → `raise AstronomicalError(`
3. Both/neither `raise ValueError(` (~line 104) → `raise ConfigurationError(`
4. Unknown polar rule `raise ValueError(f"Unknown polar circle rule` → `raise ConfigurationError(`
5. Unknown madhab guard `raise ValueError(f"Unknown madhab` → `raise ConfigurationError(`
6. Undefined-Asr `raise RuntimeError(` → `raise AstronomicalError(`
7. Unknown prayer `raise ValueError(f"Unknown prayer` → `raise ConfigurationError(`
8. Unreachable no-valid-date guard `raise RuntimeError(` → `raise AstronomicalError(`
9. isha-interval control-flow `raise ValueError("Isha interval is either not defined` — DO NOT TOUCH. Add directly above it (12-space indent, try-body level, black-clean):
```python
        # NOTE: stays ValueError on purpose - the except (ValueError,
        # TypeError) below depends on this exact type to switch to
        # angle-based Isha. Not part of the public error tree.
```

- [ ] **Step 1: Update the affected tests first (TDD: they fail before the swap)**

In `tests/test_PrayerTimes.py`: add `from alfalak.exceptions import AstronomicalError, ConfigurationError`; change line 44 `pytest.raises(ValueError,` → `pytest.raises(ConfigurationError,`; lines 59, 69 `pytest.raises(RuntimeError)` → `pytest.raises(AstronomicalError)`; line 268 `pytest.raises(RuntimeError, match="(?i)polar")` → `pytest.raises(AstronomicalError, match="(?i)polar")`; rename `test_invalid_madhab_raises_value_error` → `test_invalid_madhab_raises_configuration_error` and change its `pytest.raises(ValueError)` → `pytest.raises(ConfigurationError)`.
In `tests/test_PolarCircle.py`: add `from alfalak.exceptions import ConfigurationError`; line 94 `pytest.raises(ValueError, match="(?i)polar")` → `pytest.raises(ConfigurationError, match="(?i)polar")`. (The construction test `test_invalid_polar_rule_type_raises_at_construction` is Task 3 scope — it constructs `CalculationParameters` directly. Leave it on `TypeError` here.)

- [ ] **Step 2: Run to verify they fail**

Run: `/tmp/opencode/adhan-bump/bin/python -m pytest tests/test_PrayerTimes.py tests/test_PolarCircle.py -q -p no:cacheprovider --no-cov`
Expected: FAIL (old builtins raised, new types expected)

- [ ] **Step 3: Apply the 9 src edits above**

- [ ] **Step 4: Run to verify they pass**

Run: same command as Step 2
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alfalak/PrayerTimes.py tests/test_PrayerTimes.py tests/test_PolarCircle.py
git commit -m "feat: migrate PrayerTimes to AlFalakError tree (issue #7)"
```

### Task 3: Migrate CalculationParameters raise sites

**Files:**
- Modify: `src/alfalak/calculation/CalculationParameters.py`
- Modify: `tests/calculation/test_CalculationParameters.py`
- Modify: `tests/test_validation.py`

Exact swaps in `src/alfalak/calculation/CalculationParameters.py`:

1. Add import: `from alfalak.exceptions import ConfigurationError, ValidationError`
2. Bad method `raise TypeError(` → `raise ConfigurationError(`
3. Bad polar-circle-rule `raise TypeError(` → `raise ConfigurationError(`
4. Fajr/isha angle `raise ValueError(` (×2) → `raise ValidationError(`
5. Negative isha interval `raise ValueError(` → `raise ValidationError(`
6. Invalid high-latitude rule `raise ValueError("Invalid high latitude rule")` → `raise ConfigurationError("Invalid high latitude rule")`

- [ ] **Step 1: Update tests first**

In `tests/calculation/test_CalculationParameters.py`: line 65 `pytest.raises(ValueError, match="Invalid high latitude rule")` → `pytest.raises(ConfigurationError, match="Invalid high latitude rule")`; line 107 `pytest.raises((TypeError, ValueError))` → `pytest.raises(ConfigurationError)`.
In `tests/test_validation.py`: add `from alfalak.exceptions import ValidationError`; lines 20, 25 `pytest.raises(ValueError, match="(?i)latitude|longitude")` → `pytest.raises(ValidationError, match="(?i)latitude|longitude")`; line 44 `pytest.raises(ValueError, match="(?i)angle|interval")` → `pytest.raises(ValidationError, match="(?i)angle|interval")`.
In `tests/test_PolarCircle.py`: `test_invalid_polar_rule_type_raises_at_construction` line 99 `pytest.raises(TypeError, match="(?i)polar")` → `pytest.raises(ConfigurationError, match="(?i)polar")` (moved here from Task 2 — it constructs `CalculationParameters` directly).

- [ ] **Step 2: Run to verify they fail**

Run: `/tmp/opencode/adhan-bump/bin/python -m pytest tests/calculation/test_CalculationParameters.py tests/test_validation.py tests/test_PolarCircle.py -q -p no:cacheprovider --no-cov`
Expected: FAIL

- [ ] **Step 3: Apply the 6 src edits above**

- [ ] **Step 4: Run to verify they pass**

Run: same command as Step 2
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alfalak/calculation/CalculationParameters.py tests/calculation/test_CalculationParameters.py tests/test_validation.py tests/test_PolarCircle.py
git commit -m "feat: migrate CalculationParameters to AlFalakError tree (issue #7)"
```

### Task 4: Migrate Madhab, Coordinates, public-api test

**Files:**
- Modify: `src/alfalak/calculation/Madhab.py`
- Modify: `src/alfalak/data/Coordinates.py`
- Modify: `tests/calculation/test_Madhab.py`
- Modify: `tests/test_public_api.py`

Exact swaps:

1. `src/alfalak/calculation/Madhab.py`: add `from alfalak.exceptions import ConfigurationError`; change `raise ValueError(f"Unknown madhab: {self!r}")` → `raise ConfigurationError(f"Unknown madhab: {self!r}")`.
2. `src/alfalak/data/Coordinates.py`: add `from alfalak.exceptions import ValidationError`; change both range `raise ValueError(` → `raise ValidationError(` (messages unchanged).
3. `tests/calculation/test_Madhab.py` line 14: `pytest.raises(ValueError, match="(?i)madhab")` → `pytest.raises(ConfigurationError, match="(?i)madhab")`.
4. `tests/test_public_api.py` line 94: `pytest.raises(ValueError, match="(?i)prayer")` → `pytest.raises(ConfigurationError, match="(?i)prayer")`; add the two imports used above to that file's import block (`ConfigurationError` alongside existing imports).
5. `tests/test_validation.py` coordinate hunks (moved here from Task 3 — they cover `Coordinates` raise sites): lines 20, 25 `pytest.raises(ValueError, match="(?i)latitude|longitude")` → `pytest.raises(ValidationError, match="(?i)latitude|longitude")`. (The parameters hunk at line 44 already migrated in Task 3; the `ValidationError` import is already present.)

- [ ] **Step 1: Update the three test files first**
- [ ] **Step 2: Run to verify they fail**

Run: `/tmp/opencode/adhan-bump/bin/python -m pytest tests/calculation/test_Madhab.py tests/test_public_api.py tests/test_validation.py -q -p no:cacheprovider --no-cov`
Expected: FAIL

- [ ] **Step 3: Apply the src swaps**
- [ ] **Step 4: Run to verify they pass**

Run: same command as Step 2
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alfalak/calculation/Madhab.py src/alfalak/data/Coordinates.py tests/calculation/test_Madhab.py tests/test_public_api.py tests/test_validation.py
git commit -m "feat: migrate Madhab/Coordinates to AlFalakError tree (issue #7)"
```

### Task 5: Exports, version, docs

**Files:**
- Modify: `src/alfalak/__init__.py`
- Modify: `pyproject.toml`
- Modify: `docs/api.md`
- Modify: `docs/migration.md`
- Modify: `CHANGES.md`

- [ ] **Step 1: Export the tree**

In `src/alfalak/__init__.py`, after the `Prayer` import line add:
```python
from alfalak.exceptions import (
    AlFalakError,
    AstronomicalError,
    ConfigurationError,
    ValidationError,
)
```
and prepend the four names to `__all__` (before `"PrayerTimes"`).

- [ ] **Step 2: Bump the version**

In `pyproject.toml`: `version = "1.0.5"` → `version = "2.0.0"`.

- [ ] **Step 3: Document**

Append to `docs/api.md`:
```markdown
## Errors

`AlFalakError` is the base for all library errors (importable from the
`alfalak` root). Subclasses: `AstronomicalError` (polar day/night,
undefined Asr), `ConfigurationError` (bad method/madhab/polar rule/
prayer/high-latitude rule, method-vs-parameters exclusivity),
`ValidationError` (out-of-range coordinates, angles, intervals).
The isha-interval `ValueError` is internal control-flow and unchanged.
```
Append to `docs/migration.md`:
```markdown
## 2.0.0 breaking change: AlFalakError tree

Failures previously raised builtin `RuntimeError`/`ValueError`/
`TypeError` now raise `AlFalakError` subclasses (`AstronomicalError`,
`ConfigurationError`, `ValidationError`) with identical messages.
Before: `except RuntimeError:` / After: `except alfalak.AstronomicalError:`.
```
In `CHANGES.md`, add at the top:
```markdown
## 2.0.0
* Breaking: dedicated `AlFalakError` hierarchy replaces builtins
  (`AstronomicalError`, `ConfigurationError`, `ValidationError`);
  messages unchanged. The internal isha-interval `ValueError` is untouched.
```

- [ ] **Step 4: Run the docs-sync guard plus full suite**

Run: `/tmp/opencode/adhan-bump/bin/python -m pytest -q -p no:cacheprovider --cov=alfalak --cov-branch --cov-fail-under=95 2>&1 | tail -2`
Expected: all pass, gate passes (the guard test auto-covers the 4 new exports — if any name is missing from `docs/api.md`, it fails; the Errors section above covers all four)

- [ ] **Step 5: Commit**

```bash
git add src/alfalak/__init__.py pyproject.toml docs/api.md docs/migration.md CHANGES.md
git commit -m "chore: export error tree, bump to 2.0.0, document break (issue #7)"
```

### Task 6: Full verification and PR

- [ ] **Step 1: Run all gates**

```bash
/tmp/opencode/adhan-bump/bin/python -m black --check src/ tests/ 2>&1 | tail -1
/tmp/opencode/adhan-bump/bin/python -m ruff check src/ tests/
/tmp/opencode/adhan-bump/bin/python -m mypy src 2>&1 | tail -1
/tmp/opencode/adhan-bump/bin/python -m pytest -q -p no:cacheprovider --cov=alfalak --cov-branch --cov-fail-under=95 --cov-report=term-missing 2>&1 | tail -2
```
Expected: black clean, ruff clean, mypy clean, full suite green, gate passes.

- [ ] **Step 2: Matrix spot-check**

```bash
/tmp/opencode/adhan-bump311/bin/python -m pytest -q -p no:cacheprovider --no-cov 2>&1 | tail -1
/tmp/opencode/adhan-bump312/bin/python -m pytest -q -p no:cacheprovider --no-cov 2>&1 | tail -1
```
Expected: same pass count on both.

- [ ] **Step 3: Push and open PR**

```bash
git push -u origin feat/exception-hierarchy
gh pr create --repo nexusnv/al-falak --base dev --head feat/exception-hierarchy --title "Dedicated AlFalakError hierarchy, version 2.0.0 (issue #7)" --body "Closes #7. Clean break per approved spec; messages unchanged; isha-interval control-flow untouched."
```
