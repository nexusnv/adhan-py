"""Compare different calculation methods for the same location and date."""

from datetime import datetime
from adhan import PrayerTimes, CalculationMethod


def main() -> None:
    coordinates = (35.7750, -78.6336)
    today = datetime.now()

    methods = [
        CalculationMethod.MUSLIM_WORLD_LEAGUE,
        CalculationMethod.NORTH_AMERICA,
        CalculationMethod.EGYPTIAN,
        CalculationMethod.KARACHI,
        CalculationMethod.UMM_AL_QURA,
        CalculationMethod.DUBAI,
        CalculationMethod.MOON_SIGHTING_COMMITTEE,
        CalculationMethod.KUWAIT,
        CalculationMethod.QATAR,
        CalculationMethod.SINGAPORE,
        CalculationMethod.UOIF,
    ]

    print(f"Calculation methods comparison for {today.strftime('%Y-%m-%d')}")
    print(f"Location: ({coordinates[0]}, {coordinates[1]})")
    print()
    print(
        f"{'Method':<30} {'Fajr':>8} {'Sunrise':>8} {'Dhuhr':>8} {'Asr':>8} {'Maghrib':>8} {'Isha':>8}"
    )
    print("-" * 90)

    for method in methods:
        pt = PrayerTimes(coordinates, today, method)
        name = method.name.replace("_", " ").title()
        print(
            f"{name:<30} "
            f"{pt.fajr.strftime('%H:%M'):>8} "
            f"{pt.sunrise.strftime('%H:%M'):>8} "
            f"{pt.dhuhr.strftime('%H:%M'):>8} "
            f"{pt.asr.strftime('%H:%M'):>8} "
            f"{pt.maghrib.strftime('%H:%M'):>8} "
            f"{pt.isha.strftime('%H:%M'):>8}"
        )


if __name__ == "__main__":
    main()
