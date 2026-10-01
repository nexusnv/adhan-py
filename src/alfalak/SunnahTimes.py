from datetime import datetime, timedelta, timezone
from alfalak.PrayerTimes import PrayerTimes
from alfalak.util.CalendarUtil import rounded_minute


class SunnahTimes:
    """
    Sunnah night markers derived from prayer times.
    Ported from upstream adhan (adhan-kotlin SunnahTimes).
    """

    #: The midpoint between Maghrib and (next-day) Fajr.
    middle_of_the_night: datetime

    #: The beginning of the last third of the period between Maghrib
    #: and (next-day) Fajr, a recommended time to perform Qiyam.
    last_third_of_the_night: datetime

    def __init__(self, prayer_times: PrayerTimes) -> None:
        tomorrow = PrayerTimes(
            prayer_times.coordinates,
            prayer_times._prayer_date + timedelta(days=1),
            calculation_parameters=prayer_times.calculation_parameters,
            time_zone=prayer_times.time_zone,
        )

        # Duration arithmetic runs in UTC: wall-clock subtraction on two
        # datetimes sharing one DST-observing ZoneInfo ignores the offset
        # change, shifting markers by an hour on transition nights.
        zone = prayer_times.maghrib.tzinfo or timezone.utc
        maghrib_utc = prayer_times.maghrib.astimezone(timezone.utc)
        fajr_utc = tomorrow.fajr.astimezone(timezone.utc)
        night_duration = (fajr_utc - maghrib_utc).total_seconds()
        self.middle_of_the_night = rounded_minute(
            maghrib_utc + timedelta(seconds=int(night_duration / 2))
        ).astimezone(zone)
        self.last_third_of_the_night = rounded_minute(
            maghrib_utc + timedelta(seconds=int(night_duration * (2 / 3)))
        ).astimezone(zone)
