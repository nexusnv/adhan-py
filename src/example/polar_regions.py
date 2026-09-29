"""Polar region strategies for locations above the Arctic circle."""

from datetime import datetime
from adhan import PrayerTimes, CalculationParameters, PolarCircleRule, CalculationMethod


def main() -> None:
    # Longyearbyen, Svalbard — above the Arctic circle
    coordinates = (78.2232, 15.6267)
    today = datetime.now()

    rules = [
        (PolarCircleRule.NEAREST_LATITUDE, "Nearest Latitude (Aqrab al-Bilad)"),
        (PolarCircleRule.NEAREST_DAY, "Nearest Day (Aqrab al-Ayyam)"),
        (PolarCircleRule.MAKKAH, "Makkah"),
    ]

    print(
        f"Polar region strategies for Longyearbyen ({coordinates[0]}, {coordinates[1]})"
    )
    print(f"Date: {today.strftime('%Y-%m-%d')}")
    print()

    for rule, description in rules:
        params = CalculationParameters(
            method=CalculationMethod.MUSLIM_WORLD_LEAGUE,
            polar_circle_rule=rule,
        )
        pt = PrayerTimes(coordinates, today, calculation_parameters=params)

        print(f"  {description}:")
        print(f"    Fajr:    {pt.fajr.strftime('%H:%M')}")
        print(f"    Sunrise: {pt.sunrise.strftime('%H:%M')}")
        print(f"    Dhuhr:   {pt.dhuhr.strftime('%H:%M')}")
        print(f"    Asr:     {pt.asr.strftime('%H:%M')}")
        print(f"    Maghrib: {pt.maghrib.strftime('%H:%M')}")
        print(f"    Isha:    {pt.isha.strftime('%H:%M')}")
        print()

    # Demonstrate NONE rule raising an error
    print("  NONE rule (raises AstronomicalError):")
    try:
        params = CalculationParameters(
            method=CalculationMethod.MUSLIM_WORLD_LEAGUE,
            polar_circle_rule=PolarCircleRule.NONE,
        )
        PrayerTimes(coordinates, today, calculation_parameters=params)
        print("    Unexpectedly succeeded")
    except Exception as e:
        print(f"    {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
