"""Basic usage: compute prayer times for a location."""

from datetime import datetime
from adhan import PrayerTimes, CalculationMethod


def main() -> None:
    # Coordinates for Raleigh, NC
    coordinates = (35.7750, -78.6336)
    today = datetime.now()

    prayer_times = PrayerTimes(
        coordinates,
        today,
        CalculationMethod.NORTH_AMERICA,
    )

    print(f"Prayer times for {today.strftime('%A %d %B %Y')}:")
    print(f"  Fajr:    {prayer_times.fajr.strftime('%H:%M')}")
    print(f"  Sunrise: {prayer_times.sunrise.strftime('%H:%M')}")
    print(f"  Dhuhr:   {prayer_times.dhuhr.strftime('%H:%M')}")
    print(f"  Asr:     {prayer_times.asr.strftime('%H:%M')}")
    print(f"  Maghrib: {prayer_times.maghrib.strftime('%H:%M')}")
    print(f"  Isha:    {prayer_times.isha.strftime('%H:%M')}")


if __name__ == "__main__":
    main()
