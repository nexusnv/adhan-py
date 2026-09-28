---
title: CLI Usage
description: Use the adhan-py command-line interface for quick prayer time output.
---

# CLI Usage

adhan-py includes a command-line interface for quick terminal output.

## Basic usage

```bash
python -m adhan --latitude 35.7750 --longitude -78.6336
```

Output:
```
fajr=2026-09-29T09:58:00+00:00
sunrise=2026-09-29T11:08:00+00:00
dhuhr=2026-09-29T17:06:00+00:00
asr=2026-09-29T20:26:00+00:00
maghrib=2026-09-29T23:01:00+00:00
isha=2026-09-30T00:11:00+00:00
```

## With date and method

```bash
python -m adhan \
  --latitude 35.7750 \
  --longitude -78.6336 \
  --date 2015-07-12 \
  --method NORTH_AMERICA
```

## Options

| Option | Required | Default | Description |
|---|---|---|---|
| `--latitude` | Yes | — | Latitude (-90 to 90) |
| `--longitude` | Yes | — | Longitude (-180 to 180) |
| `--date` | No | Today | Date as YYYY-MM-DD |
| `--method` | No | MUSLIM_WORLD_LEAGUE | Calculation method |

## Available methods

```
MUSLIM_WORLD_LEAGUE
NORTH_AMERICA
EGYPTIAN
KARACHI
UMM_AL_QURA
DUBAI
MOON_SIGHTING_COMMITTEE
KUWAIT
QATAR
SINGAPORE
UOIF
```

## Error handling

The CLI exits with code 2 for invalid input:

```bash
$ python -m adhan --latitude 35 --longitude -78 --method BOGUS
usage: adhan [-h] --latitude LATITUDE --longitude LONGITUDE [--date DATE]
             [--method {MUSLIM_WORLD_LEAGUE,NORTH_AMERICA,...}]
adhan: error: argument --method: invalid choice: 'BOGUS'
```

## See also

- [Getting Started](/getting-started/) — Python API usage
- [Calculation Methods](/calculation-methods/) — method details
