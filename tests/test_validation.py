import pytest
from decimal import Decimal
from alfalak import PrayerTimes, Qibla
from alfalak.calculation import CalculationMethod, CalculationParameters
from alfalak.data.Coordinates import Coordinates
from alfalak.exceptions import AlFalakError, ValidationError
from alfalak.util.DateComponents import DateComponents


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
    with pytest.raises(ValidationError, match="(?i)latitude|longitude"):
        Coordinates(latitude, longitude)


def test_out_of_range_tuple_rejected_by_prayer_times():
    with pytest.raises(ValidationError, match="(?i)latitude|longitude"):
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


@pytest.mark.parametrize(
    "latitude, longitude",
    [("a", "b"), (None, None), (float("nan"), "b"), (True, False)],
)
def test_non_numeric_coordinates_rejected(latitude, longitude):
    with pytest.raises(ValidationError, match="(?i)real number|latitude|longitude"):
        Coordinates(latitude, longitude)


@pytest.mark.parametrize(
    "coordinates",
    [("a", "b"), (None, None), (35.7,), (), None, 35.7, (True, False)],
)
def test_malformed_coordinates_rejected_by_prayer_times(coordinates):
    with pytest.raises(ValidationError, match="(?i)coordinates|real number"):
        PrayerTimes(
            coordinates,
            DateComponents(2015, 7, 12),
            CalculationMethod.MUSLIM_WORLD_LEAGUE,
        )


def test_malformed_coordinates_rejected_by_qibla():
    with pytest.raises(ValidationError, match="(?i)coordinates|real number"):
        Qibla(("a", "b"))


def test_malformed_coordinates_are_alfalak_errors():
    try:
        PrayerTimes(
            ("a", "b"),
            DateComponents(2015, 7, 12),
            CalculationMethod.MUSLIM_WORLD_LEAGUE,
        )
    except AlFalakError:
        pass
    else:
        pytest.fail("expected AlFalakError")


def test_decimal_coordinates_normalized_to_float():
    # Coordinates accepts Decimal but downstream float arithmetic (Qibla,
    # SolarTime) cannot consume it; fields must be plain floats, never a
    # bare TypeError leaking through the AlFalakError contract.
    coords = Coordinates(Decimal("35.7750"), Decimal("-78.6336"))

    assert isinstance(coords.latitude, float)
    assert isinstance(coords.longitude, float)
    assert Qibla(
        (Decimal("35.7750"), Decimal("-78.6336"))
    ).direction == pytest.approx(Qibla((35.7750, -78.6336)).direction)
