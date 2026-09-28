import pytest
from adhanpy import PrayerTimes
from adhanpy.calculation import CalculationMethod, CalculationParameters
from adhanpy.data.Coordinates import Coordinates
from adhanpy.exceptions import ValidationError
from adhanpy.util.DateComponents import DateComponents


@pytest.mark.parametrize(
    "latitude, longitude", [(90, 0), (-90, 0), (0, 180), (0, -180), (35.77, -78.63)]
)
def test_boundary_coordinates_accepted(latitude, longitude):
    assert Coordinates(latitude, longitude).latitude == latitude


@pytest.mark.parametrize(
    "latitude, longitude",
    [(90.1, 0), (-90.1, 0), (0, 180.1), (0, -180.1), (200, 400)],
)
def test_out_of_range_coordinates_rejected(latitude, longitude):
    with pytest.raises(ValueError, match="(?i)latitude|longitude"):
        Coordinates(latitude, longitude)


def test_out_of_range_tuple_rejected_by_prayer_times():
    with pytest.raises(ValueError, match="(?i)latitude|longitude"):
        PrayerTimes(
            (91, 0),
            DateComponents(2015, 7, 12),
            CalculationMethod.MUSLIM_WORLD_LEAGUE,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"fajr_angle": -1},
        {"fajr_angle": 91},
        {"isha_angle": -1},
        {"isha_angle": 91},
        {"isha_interval": -5},
    ],
)
def test_out_of_range_parameters_rejected(kwargs):
    with pytest.raises(ValidationError, match="(?i)angle|interval"):
        CalculationParameters(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"fajr_angle": 0, "isha_angle": 0},
        {"fajr_angle": 90, "isha_angle": 90},
        {"isha_interval": 0},
        {"isha_interval": 90},
    ],
)
def test_boundary_parameters_accepted(kwargs):
    CalculationParameters(**kwargs)
