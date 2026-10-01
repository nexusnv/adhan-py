"""High latitude rules for locations with extreme night lengths."""

from datetime import datetime
from alfalak import (
    PrayerTimes,
    CalculationParameters,
    HighLatitudeRule,
    CalculationMethod,
)


def main() -> None:
    # London — high latitude with long summer nights
    coordinates = (51.5074, -0.1278)
    today = datetime.now()

    rules = [
        (HighLatitudeRule.MIDDLE_OF_THE_NIGHT, "Middle of the Night"),
        (HighLatitudeRule.SEVENTH_OF_THE_NIGHT, "Seventh of the Night"),
        (HighLatitudeRule.TWILIGHT_ANGLE, "Twilight Angle"),
    ]

    print(f"High latitude rules for London ({coordinates[0]}, {coordinates[1]})")
    print(f"Date: {today.strftime('%Y-%m-%d')}")
    print()

    for rule, description in rules:
        params = CalculationParameters(
            method=CalculationMethod.MUSLIM_WORLD_LEAGUE,
        )
        params.high_latitude_rule = rule
        pt = PrayerTimes(coordinates, today, calculation_parameters=params)

        print(f"  {description}:")
        print(f"    Fajr:    {pt.fajr.strftime('%H:%M')}")
        print(f"    Sunrise: {pt.sunrise.strftime('%H:%M')}")
        print(f"    Dhuhr:   {pt.dhuhr.strftime('%H:%M')}")
        print(f"    Asr:     {pt.asr.strftime('%H:%M')}")
        print(f"    Maghrib: {pt.maghrib.strftime('%H:%M')}")
        print(f"    Isha:    {pt.isha.strftime('%H:%M')}")
        print()


if __name__ == "__main__":
    main()
