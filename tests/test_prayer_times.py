import math
import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from alfalak.data.Coordinates import Coordinates
from alfalak.util.DateComponents import DateComponents
from alfalak.calculation.CalculationMethod import CalculationMethod
from alfalak.calculation.CalculationParameters import CalculationParameters
from alfalak.astronomy.SolarTime import SolarTime
from alfalak.util.TimeComponents import TimeComponents
from alfalak.calculation.Madhab import Madhab
from alfalak.calculation.PolarCircleRule import PolarCircleRule
from alfalak.PrayerTimes import PrayerTimes
from alfalak.calculation.PrayerAdjustments import PrayerAdjustments
from alfalak.exceptions import AstronomicalError, ConfigurationError
from zoneinfo import ZoneInfo


def test_prayer_times_raleigh_golden():
    # Arrange
    date = DateComponents(2015, 7, 12)
    params = CalculationParameters(method=CalculationMethod.NORTH_AMERICA)
    params.madhab = Madhab.HANAFI
    coordinates = (35.7750, -78.6336)
    format = "%I:%M %p"
    tz = ZoneInfo("America/New_York")

    # Act
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=params)

    # Assert
    assert prayer_times.fajr.astimezone(tz).strftime(format) == "04:42 AM"
    assert prayer_times.sunrise.astimezone(tz).strftime(format) == "06:08 AM"
    assert prayer_times.dhuhr.astimezone(tz).strftime(format) == "01:21 PM"
    assert prayer_times.asr.astimezone(tz).strftime(format) == "06:22 PM"
    assert prayer_times.maghrib.astimezone(tz).strftime(format) == "08:32 PM"
    assert prayer_times.isha.astimezone(tz).strftime(format) == "09:57 PM"


def test_either_calculation_method_or_calculation_parameters_is_passed():
    date = DateComponents(2015, 7, 12)
    method = CalculationMethod.NORTH_AMERICA
    params = CalculationParameters(method=method)
    coordinates = (35.7750, -78.6336)

    with pytest.raises(
        ConfigurationError,
        match="Only one of calculation_method or calculation_parameters must be passed.",
    ):
        PrayerTimes(coordinates, date, method, params)


def test_when_transit_or_sunrise_components_or_sunset_components_or_tomorrow_sunrise_components_is_none_it_should_raise_exception():
    date = DateComponents(2015, 7, 12)
    method = CalculationMethod.NORTH_AMERICA
    coordinates = (35.7750, -78.6336)

    with patch.object(TimeComponents, "from_float", lambda e: None):
        with pytest.raises(AstronomicalError, match="(?i)polar day/night"):
            PrayerTimes(coordinates, date, method)


def test_when_asr_is_not_set_raise_exception():
    date = DateComponents(2015, 7, 12)
    method = CalculationMethod.NORTH_AMERICA
    coordinates = (35.7750, -78.6336)

    with patch.object(SolarTime, "afternoon", lambda e, f: math.inf):
        with pytest.raises(AstronomicalError, match="Unable to compute Asr"):
            PrayerTimes(coordinates, date, method)


def test_prayer_times_with_method_with_isha_interval():
    date = DateComponents(2022, 8, 8)
    parameters = CalculationParameters(method=CalculationMethod.UMM_AL_QURA)
    coordinates = (21.422510, 39.826168)

    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=parameters)

    interval_maghrib_isha = prayer_times.isha - prayer_times.maghrib

    assert interval_maghrib_isha.total_seconds() / 60 == parameters.isha_interval


def test_offsets():
    # Arrange
    date = DateComponents(2015, 12, 1)
    coordinates = (35.7750, -78.6336)
    format = "%I:%M %p"
    tz = ZoneInfo("America/New_York")
    calculation_method = CalculationMethod.MUSLIM_WORLD_LEAGUE

    parameters_with_no_offsets = CalculationParameters(method=calculation_method)

    parameters_with_offsets = CalculationParameters(method=calculation_method)
    parameters_with_offsets.adjustments.fajr = 10
    parameters_with_offsets.adjustments.sunrise = 10
    parameters_with_offsets.adjustments.dhuhr = 10
    parameters_with_offsets.adjustments.asr = 10
    parameters_with_offsets.adjustments.maghrib = 10
    parameters_with_offsets.adjustments.isha = 10

    parameters_with_blank_adjustments = CalculationParameters(method=calculation_method)
    parameters_with_blank_adjustments.adjustments = PrayerAdjustments()

    # Act
    prayer_times_with_no_offsets = PrayerTimes(
        coordinates, date, calculation_parameters=parameters_with_no_offsets
    )
    prayer_times_with_offsets = PrayerTimes(
        coordinates, date, calculation_parameters=parameters_with_offsets
    )
    prayer_times_with_blank_adjustments = PrayerTimes(
        coordinates, date, calculation_parameters=parameters_with_blank_adjustments
    )

    # Assert
    assert (
        prayer_times_with_no_offsets.fajr.astimezone(tz).strftime(format) == "05:35 AM"
    )
    assert prayer_times_with_offsets.fajr.astimezone(tz).strftime(format) == "05:45 AM"
    assert (
        prayer_times_with_blank_adjustments.fajr.astimezone(tz).strftime(format)
        == "05:35 AM"
    )

    assert (
        prayer_times_with_no_offsets.sunrise.astimezone(tz).strftime(format)
        == "07:06 AM"
    )
    assert (
        prayer_times_with_offsets.sunrise.astimezone(tz).strftime(format) == "07:16 AM"
    )
    assert (
        prayer_times_with_blank_adjustments.sunrise.astimezone(tz).strftime(format)
        == "07:06 AM"
    )

    assert (
        prayer_times_with_no_offsets.dhuhr.astimezone(tz).strftime(format) == "12:05 PM"
    )
    assert prayer_times_with_offsets.dhuhr.astimezone(tz).strftime(format) == "12:15 PM"
    assert (
        prayer_times_with_blank_adjustments.dhuhr.astimezone(tz).strftime(format)
        == "12:05 PM"
    )

    assert (
        prayer_times_with_no_offsets.asr.astimezone(tz).strftime(format) == "02:42 PM"
    )
    assert prayer_times_with_offsets.asr.astimezone(tz).strftime(format) == "02:52 PM"
    assert (
        prayer_times_with_blank_adjustments.asr.astimezone(tz).strftime(format)
        == "02:42 PM"
    )

    assert (
        prayer_times_with_no_offsets.maghrib.astimezone(tz).strftime(format)
        == "05:01 PM"
    )
    assert (
        prayer_times_with_offsets.maghrib.astimezone(tz).strftime(format) == "05:11 PM"
    )
    assert (
        prayer_times_with_blank_adjustments.maghrib.astimezone(tz).strftime(format)
        == "05:01 PM"
    )

    assert (
        prayer_times_with_no_offsets.isha.astimezone(tz).strftime(format) == "06:26 PM"
    )
    assert prayer_times_with_offsets.isha.astimezone(tz).strftime(format) == "06:36 PM"
    assert (
        prayer_times_with_blank_adjustments.isha.astimezone(tz).strftime(format)
        == "06:26 PM"
    )


def test_moon_sighting_method():
    # Arrange
    date = DateComponents(2016, 1, 31)
    coordinates = (35.7750, -78.6336)
    calculation_method = CalculationMethod.MOON_SIGHTING_COMMITTEE
    format = "%I:%M %p"
    tz = ZoneInfo("America/New_York")

    # Act
    prayer_times = PrayerTimes(coordinates, date, calculation_method)

    # Assert
    assert prayer_times.fajr.astimezone(tz).strftime(format) == "05:48 AM"
    assert prayer_times.sunrise.astimezone(tz).strftime(format) == "07:16 AM"
    assert prayer_times.dhuhr.astimezone(tz).strftime(format) == "12:33 PM"
    assert prayer_times.asr.astimezone(tz).strftime(format) == "03:20 PM"
    assert prayer_times.maghrib.astimezone(tz).strftime(format) == "05:43 PM"
    assert prayer_times.isha.astimezone(tz).strftime(format) == "07:05 PM"


def test_moon_sighting_method_high_lat():
    # Values from http://www.moonsighting.com/pray.php
    # Arrange
    date = DateComponents(2016, 1, 1)
    parameters = CalculationParameters(method=CalculationMethod.MOON_SIGHTING_COMMITTEE)
    parameters.madhab = Madhab.HANAFI
    coordinates = (59.9094, 10.7349)
    format = "%I:%M %p"
    tz = ZoneInfo("Europe/Oslo")

    # Act
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=parameters)

    # Assert
    assert prayer_times.fajr.astimezone(tz).strftime(format) == "07:34 AM"
    assert prayer_times.sunrise.astimezone(tz).strftime(format) == "09:19 AM"
    assert prayer_times.dhuhr.astimezone(tz).strftime(format) == "12:25 PM"
    assert prayer_times.asr.astimezone(tz).strftime(format) == "01:36 PM"
    assert prayer_times.maghrib.astimezone(tz).strftime(format) == "03:25 PM"
    assert prayer_times.isha.astimezone(tz).strftime(format) == "05:02 PM"


def test_moon_sighting_method_high_lat_different_times_of_year():
    # Values from http://www.moonsighting.com/pray.php
    # Arrange
    params = CalculationParameters(method=CalculationMethod.MOON_SIGHTING_COMMITTEE)
    coordinates = (59.9094, 10.7349)
    format = "%I:%M %p"
    tz = ZoneInfo("Europe/Oslo")

    # Act, Assert
    date = DateComponents(2015, 7, 12)
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=params)
    assert prayer_times.fajr.astimezone(tz).strftime(format) == "03:26 AM"

    date = DateComponents(2015, 10, 12)
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=params)
    assert prayer_times.dhuhr.astimezone(tz).strftime(format) == "01:09 PM"

    date = DateComponents(2015, 4, 12)
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=params)
    assert prayer_times.asr.astimezone(tz).strftime(format) == "05:04 PM"

    date = DateComponents(2015, 5, 12)
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=params)
    assert prayer_times.maghrib.astimezone(tz).strftime(format) == "09:43 PM"

    date = DateComponents(2015, 9, 12)
    prayer_times = PrayerTimes(coordinates, date, calculation_parameters=params)
    assert prayer_times.isha.astimezone(tz).strftime(format) == "09:03 PM"


def test_prayer_times_second_precision_locked():
    # minute-resolution goldens cannot catch rounding drift; lock full
    # precision in UTC so future rounding changes show up here
    date = DateComponents(2015, 7, 12)
    params = CalculationParameters(method=CalculationMethod.NORTH_AMERICA)
    params.madhab = Madhab.HANAFI
    prayer_times = PrayerTimes((35.7750, -78.6336), date, calculation_parameters=params)

    assert prayer_times.fajr.strftime("%H:%M:%S") == "08:42:00"
    assert prayer_times.sunrise.strftime("%H:%M:%S") == "10:08:00"
    assert prayer_times.dhuhr.strftime("%H:%M:%S") == "17:21:00"
    assert prayer_times.asr.strftime("%H:%M:%S") == "22:22:00"
    assert prayer_times.maghrib.strftime("%H:%M:%S") == "00:32:00"
    assert prayer_times.isha.strftime("%H:%M:%S") == "01:57:00"


def test_polar_night_error_message():
    params = CalculationParameters(method=CalculationMethod.MUSLIM_WORLD_LEAGUE)
    params.polar_circle_rule = PolarCircleRule.NONE

    with pytest.raises(AstronomicalError, match="(?i)polar"):
        PrayerTimes(
            (68.35, 18.83),
            DateComponents(2015, 12, 21),
            calculation_parameters=params,
        )


def test_invalid_madhab_raises_configuration_error():
    params = CalculationParameters(method=CalculationMethod.MUSLIM_WORLD_LEAGUE)
    params.madhab = None

    with pytest.raises(ConfigurationError, match="(?i)madhab"):
        PrayerTimes(
            (35.7750, -78.6336),
            DateComponents(2015, 7, 12),
            calculation_parameters=params,
        )


def test_prayer_times_accepts_coordinates_object():
    date = DateComponents(2015, 7, 12)
    params_tuple = CalculationParameters(method=CalculationMethod.NORTH_AMERICA)
    params_coords = CalculationParameters(method=CalculationMethod.NORTH_AMERICA)

    from_tuple = PrayerTimes(
        (35.7750, -78.6336), date, calculation_parameters=params_tuple
    )
    from_object = PrayerTimes(
        Coordinates(35.7750, -78.6336), date, calculation_parameters=params_coords
    )

    assert from_object.fajr == from_tuple.fajr
    assert from_object.isha == from_tuple.isha


def test_prayer_times_accepts_datetime_and_date_components():
    params_dt = CalculationParameters(method=CalculationMethod.NORTH_AMERICA)
    params_dc = CalculationParameters(method=CalculationMethod.NORTH_AMERICA)

    from_datetime = PrayerTimes(
        (35.7750, -78.6336),
        datetime(2015, 7, 12, tzinfo=timezone.utc),
        calculation_parameters=params_dt,
    )
    from_components = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        calculation_parameters=params_dc,
    )

    assert from_components.fajr == from_datetime.fajr
    assert from_components.isha == from_datetime.isha


def test_prayer_times_timezone_conversion():
    # Arrange
    calculation_method = CalculationMethod.MOON_SIGHTING_COMMITTEE
    coordinates = (51.49799827422162, -0.1358135027951458)
    format = "%I:%M %p"
    tz = ZoneInfo("Europe/London")

    # Winter time, UTC and GMT share the same time
    date_winter = DateComponents(2022, 1, 1)

    # Summer time, BST: UTC + 1
    date_summer = DateComponents(2022, 8, 1)

    # Act,  Assert
    prayer_times = PrayerTimes(
        coordinates, date_winter, calculation_method=calculation_method
    )
    assert prayer_times.fajr.strftime(format) == "06:25 AM"

    prayer_times = PrayerTimes(
        coordinates, date_winter, calculation_method=calculation_method, time_zone=tz
    )
    assert prayer_times.fajr.strftime(format) == "06:25 AM"

    prayer_times = PrayerTimes(
        coordinates, date_summer, calculation_method=calculation_method
    )
    assert prayer_times.fajr.strftime(format) == "02:37 AM"

    prayer_times = PrayerTimes(
        coordinates, date_summer, calculation_method=calculation_method, time_zone=tz
    )
    assert prayer_times.fajr.strftime(format) == "03:37 AM"


def test_twilight_preset_definitions_locked():
    # Slice 2.1: any change to METHODS_PARAMETERS must fail loudly here.
    # (fajr_angle, isha_angle, isha_interval, fajr, sunrise, dhuhr, asr,
    # maghrib, isha method_adjustments).
    expected = {
        CalculationMethod.NONE: (0.0, 0.0, 0, (0, 0, 0, 0, 0, 0)),
        CalculationMethod.MUSLIM_WORLD_LEAGUE: (18.0, 17.0, 0, (0, 0, 1, 0, 0, 0)),
        CalculationMethod.EGYPTIAN: (19.5, 17.5, 0, (0, 0, 1, 0, 0, 0)),
        CalculationMethod.KARACHI: (18.0, 18.0, 0, (0, 0, 1, 0, 0, 0)),
        CalculationMethod.UMM_AL_QURA: (18.5, 0.0, 90, (0, 0, 0, 0, 0, 0)),
        CalculationMethod.DUBAI: (18.2, 18.2, 0, (0, -3, 3, 3, 3, 0)),
        CalculationMethod.MOON_SIGHTING_COMMITTEE: (
            18.0,
            18.0,
            0,
            (0, 0, 5, 0, 3, 0),
        ),
        CalculationMethod.NORTH_AMERICA: (15.0, 15.0, 0, (0, 0, 1, 0, 0, 0)),
        CalculationMethod.KUWAIT: (18.0, 17.5, 0, (0, 0, 0, 0, 0, 0)),
        CalculationMethod.QATAR: (18.0, 0.0, 90, (0, 0, 0, 0, 0, 0)),
        CalculationMethod.SINGAPORE: (20.0, 18.0, 0, (0, 0, 1, 0, 0, 0)),
        CalculationMethod.UOIF: (12.0, 12.0, 0, (0, 0, 0, 0, 0, 0)),
    }

    assert set(expected) == set(CalculationMethod)

    for method, (
        fajr_angle,
        isha_angle,
        isha_interval,
        adjustments,
    ) in expected.items():
        params = CalculationParameters(method=method)
        assert params.fajr_angle == fajr_angle
        assert params.isha_angle == isha_angle
        assert params.isha_interval == isha_interval
        method_adjustments = params.method_adjustments
        assert (
            method_adjustments.fajr,
            method_adjustments.sunrise,
            method_adjustments.dhuhr,
            method_adjustments.asr,
            method_adjustments.maghrib,
            method_adjustments.isha,
        ) == adjustments


def test_milestone_twilight_rows_pinned():
    # Milestone Phase 2 rows mapped to presets: MWL 18/17, Egypt 19.5/17.5,
    # ISNA 15/15 via NORTH_AMERICA, JAKIM/MUIS 20/18 via SINGAPORE.
    assert CalculationParameters(
        method=CalculationMethod.MUSLIM_WORLD_LEAGUE
    ).fajr_angle == 18.0
    assert CalculationParameters(
        method=CalculationMethod.MUSLIM_WORLD_LEAGUE
    ).isha_angle == 17.0
    assert CalculationParameters(method=CalculationMethod.EGYPTIAN).fajr_angle == 19.5
    assert CalculationParameters(method=CalculationMethod.EGYPTIAN).isha_angle == 17.5
    assert CalculationParameters(
        method=CalculationMethod.NORTH_AMERICA
    ).fajr_angle == 15.0
    assert CalculationParameters(
        method=CalculationMethod.NORTH_AMERICA
    ).isha_angle == 15.0
    assert CalculationParameters(method=CalculationMethod.SINGAPORE).fajr_angle == 20.0
    assert CalculationParameters(method=CalculationMethod.SINGAPORE).isha_angle == 18.0


@pytest.mark.parametrize(
    "method, fajr, sunrise, dhuhr, asr, maghrib, isha",
    [
        (
            CalculationMethod.NONE,
            "10:13:00",
            "10:08:00",
            "17:20:00",
            "21:09:00",
            "00:32:00",
            "00:28:00",
        ),
        (
            CalculationMethod.MUSLIM_WORLD_LEAGUE,
            "08:22:00",
            "10:08:00",
            "17:21:00",
            "21:09:00",
            "00:32:00",
            "02:11:00",
        ),
        (
            CalculationMethod.EGYPTIAN,
            "08:11:00",
            "10:08:00",
            "17:21:00",
            "21:09:00",
            "00:32:00",
            "02:14:00",
        ),
        (
            CalculationMethod.KARACHI,
            "08:22:00",
            "10:08:00",
            "17:21:00",
            "21:09:00",
            "00:32:00",
            "02:18:00",
        ),
        (
            CalculationMethod.UMM_AL_QURA,
            "08:18:00",
            "10:08:00",
            "17:20:00",
            "21:09:00",
            "00:32:00",
            "02:02:00",
        ),
        (
            CalculationMethod.DUBAI,
            "08:20:00",
            "10:05:00",
            "17:23:00",
            "21:12:00",
            "00:35:00",
            "02:19:00",
        ),
        (
            CalculationMethod.MOON_SIGHTING_COMMITTEE,
            "08:26:00",
            "10:08:00",
            "17:25:00",
            "21:09:00",
            "00:35:00",
            "01:47:00",
        ),
        (
            CalculationMethod.NORTH_AMERICA,
            "08:42:00",
            "10:08:00",
            "17:21:00",
            "21:09:00",
            "00:32:00",
            "01:57:00",
        ),
        (
            CalculationMethod.KUWAIT,
            "08:22:00",
            "10:08:00",
            "17:20:00",
            "21:09:00",
            "00:32:00",
            "02:14:00",
        ),
        (
            CalculationMethod.QATAR,
            "08:22:00",
            "10:08:00",
            "17:20:00",
            "21:09:00",
            "00:32:00",
            "02:02:00",
        ),
        (
            CalculationMethod.SINGAPORE,
            "08:07:00",
            "10:08:00",
            "17:21:00",
            "21:09:00",
            "00:32:00",
            "02:18:00",
        ),
        (
            CalculationMethod.UOIF,
            "09:02:00",
            "10:08:00",
            "17:20:00",
            "21:09:00",
            "00:32:00",
            "01:38:00",
        ),
    ],
)
def test_twilight_preset_goldens_raleigh(method, fajr, sunrise, dhuhr, asr, maghrib, isha):
    # One golden day per method: Raleigh (35.7750, -78.6336), 2015-07-12, UTC.
    # Angle-vs-interval mode is asserted below for UMM_AL_QURA/QATAR.
    prayer_times = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        calculation_method=method,
    )

    assert prayer_times.fajr.strftime("%H:%M:%S") == fajr
    assert prayer_times.sunrise.strftime("%H:%M:%S") == sunrise
    assert prayer_times.dhuhr.strftime("%H:%M:%S") == dhuhr
    assert prayer_times.asr.strftime("%H:%M:%S") == asr
    assert prayer_times.maghrib.strftime("%H:%M:%S") == maghrib
    assert prayer_times.isha.strftime("%H:%M:%S") == isha

    if method in (CalculationMethod.UMM_AL_QURA, CalculationMethod.QATAR):
        assert (prayer_times.isha - prayer_times.maghrib).total_seconds() / 60 == 90
    elif method is not CalculationMethod.NONE:
        assert (
            prayer_times.fajr
            <= prayer_times.sunrise
            <= prayer_times.dhuhr
            <= prayer_times.asr
            <= prayer_times.maghrib
            <= prayer_times.isha
        )
