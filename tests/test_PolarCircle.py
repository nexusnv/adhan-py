import pytest
from datetime import date
from adhan import PrayerTimes
from adhan.calculation import (
    CalculationMethod,
    CalculationParameters,
    PolarCircleRule,
)
from adhan.data.Coordinates import Coordinates
from adhan.exceptions import ConfigurationError
from adhan.Qibla import MAKKAH
from adhan.util.DateComponents import DateComponents

TROMSO = (69.65, 18.96)
SUMMER = DateComponents(2015, 6, 21)
WINTER = DateComponents(2015, 12, 21)


def _params(**kwargs):
    return CalculationParameters(method=CalculationMethod.MUSLIM_WORLD_LEAGUE, **kwargs)


def _ordered(prayer_times):
    # Only Dhuhr/Asr may coincide (documented saturation); every other
    # adjacent pair is strictly increasing on all covered cases.
    return (
        prayer_times.fajr
        < prayer_times.sunrise
        < prayer_times.dhuhr
        <= prayer_times.asr
        < prayer_times.maghrib
        < prayer_times.isha
    )


@pytest.mark.parametrize("date", [SUMMER, WINTER])
def test_default_assumes_nearest_latitude(date):
    prayer_times = PrayerTimes(TROMSO, date, calculation_parameters=_params())

    assert _ordered(prayer_times)
    # clamped toward the equator, near the solstice boundary (~66.5)
    assert 60 < prayer_times.coordinates.latitude < TROMSO[0]
    assert prayer_times.coordinates.longitude == TROMSO[1]


def test_nearest_day_keeps_location_but_shifts_date():
    prayer_times = PrayerTimes(
        TROMSO,
        WINTER,
        calculation_parameters=_params(polar_circle_rule=PolarCircleRule.NEAREST_DAY),
    )

    assert _ordered(prayer_times)
    assert prayer_times.coordinates.latitude == TROMSO[0]
    assert prayer_times.fajr.date() != date(2015, 12, 21)


def test_makkah_rule_matches_makkah_schedule():
    polar = PrayerTimes(
        TROMSO,
        WINTER,
        calculation_parameters=_params(polar_circle_rule=PolarCircleRule.MAKKAH),
    )
    makkah = PrayerTimes(
        (MAKKAH.latitude, MAKKAH.longitude),
        WINTER,
        calculation_parameters=_params(polar_circle_rule=PolarCircleRule.MAKKAH),
    )

    assert polar.coordinates.latitude == MAKKAH.latitude
    for name in ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"):
        assert getattr(polar, name) == getattr(makkah, name)


def test_no_rule_change_on_normal_days():
    normal_default = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        calculation_parameters=_params(),
    )
    normal_none = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        calculation_parameters=_params(polar_circle_rule=PolarCircleRule.NONE),
    )

    for name in ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"):
        assert getattr(normal_default, name) == getattr(normal_none, name)


def test_unknown_polar_rule_raises():
    params = _params()
    params.polar_circle_rule = "bogus"

    with pytest.raises(ConfigurationError, match="(?i)polar"):
        PrayerTimes(TROMSO, WINTER, calculation_parameters=params)


def test_invalid_polar_rule_type_raises_at_construction():
    with pytest.raises(ConfigurationError, match="(?i)polar"):
        CalculationParameters(
            method=CalculationMethod.MUSLIM_WORLD_LEAGUE,
            polar_circle_rule="bogus",
        )


def test_coordinates_object_accepted_for_polar():
    prayer_times = PrayerTimes(
        Coordinates(*TROMSO), SUMMER, calculation_parameters=_params()
    )

    assert _ordered(prayer_times)


def test_asr_saturates_to_dhuhr_at_polar_boundary():
    # 66.4N on 2015-12-21 computes Asr before Dhuhr without the clamp
    prayer_times = PrayerTimes(
        (66.4, 18.96),
        DateComponents(2015, 12, 21),
        calculation_parameters=_params(polar_circle_rule=PolarCircleRule.NONE),
    )

    assert prayer_times.asr == prayer_times.dhuhr


def test_extreme_adjustments_saturate_asr_to_dhuhr():
    params = _params()
    params.adjustments.dhuhr = 180
    prayer_times = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 12, 1),
        calculation_parameters=params,
    )

    assert prayer_times.asr == prayer_times.dhuhr
    assert _ordered(prayer_times)
