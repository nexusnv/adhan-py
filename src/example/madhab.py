"""Madhab selection: Shafi vs Hanafi Asr calculation."""

from datetime import datetime
from adhan import PrayerTimes, CalculationParameters, Madhab, CalculationMethod


def main() -> None:
    coordinates = (35.7750, -78.6336)
    today = datetime.now()

    madhabs = [
        (Madhab.SHAFI, "Shafi (default)"),
        (Madhab.HANAFI, "Hanafi"),
    ]

    print(f"Madhab comparison for {today.strftime('%Y-%m-%d')}")
    print(f"Location: ({coordinates[0]}, {coordinates[1]})")
    print()

    for madhab, description in madhabs:
        params = CalculationParameters(
            method=CalculationMethod.MUSLIM_WORLD_LEAGUE,
        )
        params.madhab = madhab
        pt = PrayerTimes(coordinates, today, calculation_parameters=params)

        print(f"  {description}:")
        print(f"    Asr: {pt.asr.strftime('%H:%M')}")
        print()


if __name__ == "__main__":
    main()
