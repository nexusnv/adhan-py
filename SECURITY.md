# Security Policy

## Supported Versions

Only the latest `1.x` release (and `main` between releases) receives
security fixes. Upstream `adhanpy` (`<= 1.0.5`) is a separate package
with its own maintenance and is out of scope here.

| Version | Supported          |
| ------- | ------------------ |
| `al-falak` `1.x` latest (this release line; identify builds by tag/commit) | :white_check_mark: |
| Upstream `adhanpy` releases and any pre-fork mirrors | :x: |

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
- Dependabot `target-branch: main` covers version updates only; security
  updates land on the default branch (`main`) like any other change.
- The prayer-time math is deterministic and offline; the realistic
  threat model is supply-chain (compromised dev dependency or action)
  and correctness (wrong times), not remote exploitation.
