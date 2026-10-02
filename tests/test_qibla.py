import math

import pytest
from alfalak import Qibla
from alfalak.data.Constants import EARTH_MEAN_RADIUS_KM
from alfalak.data.Coordinates import Coordinates
from alfalak.exceptions import ValidationError
from alfalak.Qibla import MAKKAH


@pytest.mark.parametrize(
    "latitude, longitude, expected",
    [
        (35.7750, -78.6336, 55.825),  # Raleigh, US
        (40.7128, -74.0060, 58.482),  # New York, US
        (51.5074, -0.1278, 118.987),  # London, UK
        (30.0444, 31.2357, 136.137),  # Cairo, EG
        (3.1390, 101.6869, 292.538),  # Kuala Lumpur, MY
        (-6.2088, 106.8456, 295.152),  # Jakarta, ID
        (-33.8688, 151.2093, 277.500),  # Sydney, AU
    ],
)
def test_qibla_direction(latitude, longitude, expected):
    # formula ported from upstream adhan (adhan-kotlin QiblaUtil);
    # cross-checked against published qibla bearings and WGS84 geodesics
    assert Qibla((latitude, longitude)).direction == pytest.approx(expected, abs=1e-2)


def test_qibla_accepts_coordinates_object():
    assert Qibla(Coordinates(35.7750, -78.6336)).direction == pytest.approx(
        Qibla((35.7750, -78.6336)).direction
    )


def test_qibla_direction_in_range():
    for latitude, longitude in [(35.7750, -78.6336), (-33.8688, 151.2093)]:
        assert 0 <= Qibla((latitude, longitude)).direction < 360


@pytest.mark.parametrize("coordinates", [None, 35.7, (), (35.7,)])
def test_qibla_malformed_coordinates_rejected(coordinates):
    with pytest.raises(ValidationError, match="(?i)coordinates|real number"):
        Qibla(coordinates)


def test_qibla_makkah_self_bearing_no_raise():
    direction = Qibla((MAKKAH.latitude, MAKKAH.longitude)).direction
    assert 0 <= direction < 360
    assert not math.isnan(direction)


# Exact antipode of the stored Makkah coordinate (derived, not literal, so a
# future re-canonicalization of MAKKAH keeps testing the true antipode).
ANTIPODE_OF_MAKKAH = (-MAKKAH.latitude, MAKKAH.longitude - 180)


def test_qibla_true_antipode_bearing_no_raise():
    direction = Qibla(ANTIPODE_OF_MAKKAH).direction
    assert 0 <= direction < 360
    assert not math.isnan(direction)


@pytest.mark.parametrize(
    "latitude, longitude, expected",
    [
        (35.7750, -78.6336, 10944),  # Raleigh, US
        (40.7128, -74.0060, 10306),  # New York, US
        (3.1390, 101.6869, 6974),  # Kuala Lumpur, MY
        (-33.8688, 151.2093, 13236),  # Sydney, AU
    ],
)
def test_qibla_distance_to_makkah_km(latitude, longitude, expected):
    # Spherical great-circle with R = 6371.0088 km, cross-checked via an
    # independent vector dot-product computation (agreement <0.02 km);
    # +/-10 km documents the radius-convention tolerance, not precision.
    assert Qibla(
        (latitude, longitude)
    ).distance_to_makkah_km == pytest.approx(expected, abs=10.0)


def test_qibla_distance_self_is_zero():
    assert Qibla(
        (MAKKAH.latitude, MAKKAH.longitude)
    ).distance_to_makkah_km == pytest.approx(0.0, abs=1e-6)


def test_qibla_distance_antipode_near_half_circumference():
    distance = Qibla(ANTIPODE_OF_MAKKAH).distance_to_makkah_km
    assert distance == pytest.approx(math.pi * EARTH_MEAN_RADIUS_KM, abs=1.0)
    assert not math.isnan(distance)
