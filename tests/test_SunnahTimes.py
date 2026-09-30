from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from adhan import PrayerTimes, SunnahTimes
from adhan.calculation import CalculationMethod, CalculationParameters
from adhan.util.DateComponents import DateComponents


def _prayer_times():
    return PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        CalculationMethod.MUSLIM_WORLD_LEAGUE,
    )


def test_sunnah_times():
    prayer_times = _prayer_times()
    sunnah_times = SunnahTimes(prayer_times)

    assert sunnah_times.middle_of_the_night == datetime(
        2015, 7, 13, 4, 28, tzinfo=timezone.utc
    )
    assert sunnah_times.last_third_of_the_night == datetime(
        2015, 7, 13, 5, 46, tzinfo=timezone.utc
    )


def test_sunnah_times_ordering():
    prayer_times = _prayer_times()
    sunnah_times = SunnahTimes(prayer_times)
    tomorrow = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 13),
        calculation_parameters=CalculationParameters(
            method=CalculationMethod.MUSLIM_WORLD_LEAGUE
        ),
    )

    assert prayer_times.maghrib < sunnah_times.middle_of_the_night
    assert sunnah_times.middle_of_the_night < sunnah_times.last_third_of_the_night
    assert sunnah_times.last_third_of_the_night < tomorrow.fajr


def test_sunnah_times_across_dst_transition():
    # US springs forward on 2015-03-08 (02:00 EST -> 03:00 EDT); duration
    # math must use absolute elapsed time, not wall-clock subtraction
    tz = ZoneInfo("America/New_York")
    prayer_times = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 3, 7),
        CalculationMethod.MUSLIM_WORLD_LEAGUE,
        time_zone=tz,
    )
    sunnah_times = SunnahTimes(prayer_times)

    assert sunnah_times.middle_of_the_night == datetime(2015, 3, 7, 23, 43, tzinfo=tz)
    assert sunnah_times.last_third_of_the_night == datetime(
        2015, 3, 8, 1, 32, tzinfo=tz
    )
