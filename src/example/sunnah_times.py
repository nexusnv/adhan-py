"""Sunnah night markers: middle and last third of the night."""

from datetime import datetime
from zoneinfo import ZoneInfo
from alfalak import PrayerTimes, SunnahTimes, CalculationMethod


def main() -> None:
    coordinates = (35.7750, -78.6336)
    tz = ZoneInfo("America/New_York")
    today = datetime.now()

    prayer_times = PrayerTimes(
        coordinates,
        today,
        CalculationMethod.MUSLIM_WORLD_LEAGUE,
        time_zone=tz,
    )
    sunnah = SunnahTimes(prayer_times)

    print(f"Sunnah times for {today.strftime('%A %d %B %Y')}:")
    print(f"  Maghrib:              {prayer_times.maghrib.strftime('%H:%M')}")
    print(f"  Middle of the night:  {sunnah.middle_of_the_night.strftime('%H:%M')}")
    print(f"  Last third:           {sunnah.last_third_of_the_night.strftime('%H:%M')}")
    print(f"  Fajr (next day):      {prayer_times.fajr.strftime('%H:%M')}")


if __name__ == "__main__":
    main()
