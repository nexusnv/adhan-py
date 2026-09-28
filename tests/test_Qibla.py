import pytest
from adhan import Qibla
from adhan.data.Coordinates import Coordinates


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
