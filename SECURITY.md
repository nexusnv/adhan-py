# Security Policy

## Supported Versions

Only the latest state of the `dev` branch (and any `1.x` release cut
from it) receives security fixes. The `master` branch mirrors upstream
and is intentionally untouched.

| Version | Supported          |
| ------- | ------------------ |
| `dev` branch latest (unreleased; the version string still reads `1.0.5` until the next release is cut — identify builds by branch/commit, not version) | :white_check_mark: |
| Upstream releases `<= 1.0.5` and the `master` mirror | :x: |

## Reporting a Vulnerability

Please do **not** open a public issue. Use GitHub's private
vulnerability reporting: the repository's **Security** tab →
**Report a vulnerability**. Reports are triaged on a best-effort basis;
expect an initial response within 14 days.

## Scope Notes

- The library declares **zero runtime dependencies** (stdlib only).
  Platform note: IANA time-zone resolution on Windows needs the external
  `tzdata` database (see README) — that is an environment requirement,
  not a declared package dependency. Please keep declared runtime
  dependencies at zero.
- Dependabot `target-branch: dev` covers version updates only; security
  updates land on the default branch (`master` mirror) and maintainers
  retarget them to `dev` before merge.
- The prayer-time math is deterministic and offline; the realistic
  threat model is supply-chain (compromised dev dependency or action)
  and correctness (wrong times), not remote exploitation.
