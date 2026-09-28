import pytest

import adhan
from adhan import PrayerTimes as RootPrayerTimes
from adhan import Qibla, SunnahTimes
from adhan.exceptions import (
    AdhanError,
    AstronomicalError,
    ConfigurationError,
    ValidationError,
)
from adhan.calculation import (
    CalculationMethod,
    CalculationParameters,
    HighLatitudeRule,
    Madhab,
    PolarCircleRule,
    PrayerAdjustments,
)
from adhan.data import Coordinates, NightPortions, Prayer, ShadowLength
from adhan.PrayerTimes import PrayerTimes
from adhan.util.DateComponents import DateComponents


def test_root_exports_match_all():
    assert getattr(adhan, "__all__") == [
        "AdhanError",
        "AstronomicalError",
        "ConfigurationError",
        "ValidationError",
        "PrayerTimes",
        "Qibla",
        "SunnahTimes",
        "CalculationMethod",
        "CalculationParameters",
        "HighLatitudeRule",
        "Madhab",
        "PolarCircleRule",
        "PrayerAdjustments",
        "Coordinates",
        "Prayer",
    ]
    assert {
        "AdhanError": AdhanError,
        "AstronomicalError": AstronomicalError,
        "ConfigurationError": ConfigurationError,
        "ValidationError": ValidationError,
        "PrayerTimes": PrayerTimes,
        "Qibla": Qibla,
        "SunnahTimes": SunnahTimes,
        "CalculationMethod": CalculationMethod,
        "CalculationParameters": CalculationParameters,
        "HighLatitudeRule": HighLatitudeRule,
        "Madhab": Madhab,
        "PolarCircleRule": PolarCircleRule,
        "PrayerAdjustments": PrayerAdjustments,
        "Coordinates": Coordinates,
        "Prayer": Prayer,
    } == {name: getattr(adhan, name) for name in adhan.__all__}
    assert adhan.PrayerTimes is RootPrayerTimes


def test_subpackage_exports():
    from adhan import calculation, data

    assert {
        "CalculationMethod": CalculationMethod,
        "CalculationParameters": CalculationParameters,
        "HighLatitudeRule": HighLatitudeRule,
        "Madhab": Madhab,
        "PolarCircleRule": PolarCircleRule,
        "PrayerAdjustments": PrayerAdjustments,
    } == {name: getattr(calculation, name) for name in calculation.__all__}
    assert {
        "Coordinates": Coordinates,
        "NightPortions": NightPortions,
        "Prayer": Prayer,
        "ShadowLength": ShadowLength,
    } == {name: getattr(data, name) for name in data.__all__}


def test_time_for_prayer_matches_attributes():
    prayer_times = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        calculation_parameters=CalculationParameters(
            method=CalculationMethod.NORTH_AMERICA
        ),
    )

    assert prayer_times.time_for_prayer(Prayer.FAJR) == prayer_times.fajr
    assert prayer_times.time_for_prayer(Prayer.SUNRISE) == prayer_times.sunrise
    assert prayer_times.time_for_prayer(Prayer.DHUHR) == prayer_times.dhuhr
    assert prayer_times.time_for_prayer(Prayer.ASR) == prayer_times.asr
    assert prayer_times.time_for_prayer(Prayer.MAGHRIB) == prayer_times.maghrib
    assert prayer_times.time_for_prayer(Prayer.ISHA) == prayer_times.isha


def test_time_for_prayer_rejects_none():
    prayer_times = PrayerTimes(
        (35.7750, -78.6336),
        DateComponents(2015, 7, 12),
        calculation_parameters=CalculationParameters(
            method=CalculationMethod.NORTH_AMERICA
        ),
    )

    with pytest.raises(ConfigurationError, match="(?i)prayer"):
        prayer_times.time_for_prayer(Prayer.NONE)


def test_docs_cover_public_api():
    # docs/api.md must name every public export or the reference rots;
    # word boundaries so Prayer is not satisfied by PrayerTimes
    import re
    from pathlib import Path

    api_docs = (Path(__file__).resolve().parent.parent / "docs" / "api.md").read_text(
        encoding="utf-8"
    )

    for name in adhan.__all__:
        assert re.search(rf"\b{name}\b", api_docs), name
    for name in ("time_for_prayer", "Qibla", "SunnahTimes"):
        assert re.search(rf"\b{name}\b", api_docs), name
