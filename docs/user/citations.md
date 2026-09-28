---
title: Citations
description: Attribution and references for adhan-py.
---

# Citations

## Original authors and projects

- **batoulapps** — Original `adhan` library in [Java](https://github.com/batoulapps/adhan-java), [JavaScript](https://github.com/batoulapps/adhan-js), [Swift](https://github.com/batoulapps/adhan-swift), and [Kotlin](https://github.com/batoulapps/adhan-kotlin). The astronomical calculation methods, formulas, and overall architecture are derived from these implementations.
- **alphahm** — Original [adhanpy](https://github.com/alphahm/adhanpy) Python port. This fork continues from that work.

## Astronomical calculation sources

The prayer time calculation methods, mathematical formulas, and computational steps are derived from:

- **Jean Meeus** — *Astronomical Algorithms* (2nd ed., Willmann-Bell, 1998). The core astronomical formulas for solar position, equation of time, and hour angle calculations.
- **US Naval Observatory (USNO)** — Solar position algorithms and twilight calculations. Reference: [aa.usno.navy.mil](https://aa.usno.navy.mil/)
- **PrayTimes.org** — Standard prayer time calculation methods and Fajr/Isha angle conventions. Reference: [praytimes.org](https://praytimes.org/)

## Calculation method sources

| Method | Source |
|---|---|
| Muslim World League | Fajr angle 18°, Isha angle 17° |
| ISNA (North America) | Fajr angle 15°, Isha angle 15° |
| Egyptian | Fajr angle 19.5°, Isha angle 17.5° |
| Karachi | Fajr angle 18°, Isha angle 18° |
| Umm al-Qura | Fajr angle 18.5°, Isha interval 90 minutes |
| Moonsighting Committee | Fajr angle 18°, Isha angle 18°, seasonal adjustments |
| Kuwait | Fajr angle 18°, Isha angle 17.5° |
| Qatar | Fajr angle 18°, Isha interval 90 minutes |
| Singapore | Fajr angle 20°, Isha angle 18° |
| UOIF | Fajr angle 12°, Isha angle 12° |

## License

This project is licensed under the MIT License — see [LICENSE](https://github.com/nexusnv/adhan-py/blob/main/LICENSE) for details.
