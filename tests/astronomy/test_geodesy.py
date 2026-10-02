"""Tests for the vendored Karney inverse on WGS84.

Reference values: GeographicLib 2.1 (Charles Karney), generated 2026-10-03
via ``Geodesic.WGS84.Inverse`` into Makkah (21.4225241, 39.8261818).
The vendored implementation is verified bit-identical to that oracle on a
320-case sweep (fixed city/pole/antipode/near-antipodal/edge points plus
300 seeded random points); the tolerances below encode the slice acceptance bar
(<=1e-6 deg / <=1 m), not the observed agreement.
"""

import math

import pytest
from alfalak.astronomy.Geodesy import (
    WGS84_A,
    WGS84_B,
    WGS84_E2,
    WGS84_F,
    geodesic_inverse,
)
from alfalak.exceptions import ValidationError

MAKKA_LAT = 21.4225241
MAKKA_LON = 39.8261818


def test_wgs84_defining_constants_exact():
    assert WGS84_A == 6378137.0
    assert WGS84_F == pytest.approx(1 / 298.257223563)


def test_wgs84_derived_constants_consistent():
    assert WGS84_B == pytest.approx(WGS84_A * (1 - WGS84_F), rel=1e-12)
    assert WGS84_E2 == pytest.approx(WGS84_F * (2 - WGS84_F), rel=1e-12)


@pytest.mark.parametrize(
    "latitude, longitude, expected_azi, expected_s12",
    [
        (35.7750, -78.6336, 55.739246718, 10961845.992388),  # Raleigh
        (40.7128, -74.0060, 58.396026135, 10323912.652457),  # New York
        (51.5074, -0.1278, 118.868402852, 4794752.668858),  # London
        (30.0444, 31.2357, 135.982352393, 1285592.277039),  # Cairo
        (3.1390, 101.6869, -67.557623661, 6979153.497455),  # Kuala Lumpur
        (-6.2088, 106.8456, -64.975302310, 7922244.964121),  # Jakarta
        (-33.8688, 151.2093, -82.681155653, 13236950.906872),  # Sydney
    ],
)
def test_inverse_city_goldens(latitude, longitude, expected_azi, expected_s12):
    azi, s12 = geodesic_inverse(latitude, longitude, MAKKA_LAT, MAKKA_LON)
    assert azi == pytest.approx(expected_azi, abs=1e-6)
    assert s12 == pytest.approx(expected_s12, abs=1.0)
    assert not math.isnan(azi) and not math.isnan(s12)


def test_inverse_near_antipodal_converges():
    # Vincenty's documented failure regime; Karney must converge.
    azi, s12 = geodesic_inverse(-20.4, -139.2, MAKKA_LAT, MAKKA_LON)
    assert azi == pytest.approx(31.740215702, abs=1e-6)
    assert s12 == pytest.approx(19862471.480885, abs=1.0)


def test_inverse_true_antipode_no_raise():
    azi, s12 = geodesic_inverse(-MAKKA_LAT, MAKKA_LON - 180, MAKKA_LAT, MAKKA_LON)
    assert s12 == pytest.approx(20003931.458625, abs=1.0)
    assert not math.isnan(azi)


def test_inverse_coincident_returns_zero_distance():
    azi, s12 = geodesic_inverse(MAKKA_LAT, MAKKA_LON, MAKKA_LAT, MAKKA_LON)
    assert s12 == pytest.approx(0.0, abs=1e-9)
    assert not math.isnan(azi)


@pytest.mark.parametrize(
    "latitude, longitude, expected_azi, expected_s12",
    [
        (90.0, 0.0, 140.1738182, 7632107.081517),
        (-90.0, 0.0, 39.8261818, 12371824.377108),
    ],
    ids=["north-pole", "south-pole"],
)
def test_inverse_poles(latitude, longitude, expected_azi, expected_s12):
    azi, s12 = geodesic_inverse(latitude, longitude, MAKKA_LAT, MAKKA_LON)
    assert azi == pytest.approx(expected_azi, abs=1e-6)
    assert s12 == pytest.approx(expected_s12, abs=1.0)


@pytest.mark.parametrize(
    "lat1, lon1",
    [(91.0, 0.0), (-91.0, 0.0), (float("nan"), 0.0), (0.0, float("inf"))],
    ids=["lat-91", "lat-plus-91", "lat-nan", "lon-inf"],
)
def test_inverse_rejects_bad_input(lat1, lon1):
    with pytest.raises(ValidationError, match="(?i)latitude|longitude"):
        geodesic_inverse(lat1, lon1, MAKKA_LAT, MAKKA_LON)


def test_inverse_non_convergence_raises_astronomical_error(monkeypatch):
    from alfalak.astronomy import Geodesy as GeodesyModule
    from alfalak.exceptions import AstronomicalError

    # Force immediate iteration exhaustion: the near-antipodal case needs
    # several Newton steps, so a zero budget must trip the defensive guard.
    monkeypatch.setattr(GeodesyModule, "_MAXIT2", 0)
    with pytest.raises(AstronomicalError, match="(?i)converge"):
        geodesic_inverse(-20.4, -139.2, MAKKA_LAT, MAKKA_LON)


def test_inverse_along_equator():
    # Equatorial branch: s12 = a * lam12, due-east azimuth.
    azi, s12 = geodesic_inverse(0.0, 0.0, 0.0, 90.0)
    assert azi == pytest.approx(90.0, abs=1e-9)
    assert s12 == pytest.approx(WGS84_A * math.pi / 2, abs=1e-3)


def test_inverse_short_line_uses_auxiliary_sphere():
    # Metre-scale line: exercises the really-short-line path.
    azi, s12 = geodesic_inverse(MAKKA_LAT, MAKKA_LON, 21.42253, 39.82619)
    assert 0.5 < s12 < 5.0
    assert not math.isnan(azi)


@pytest.mark.parametrize(
    "lat1, lon1, lat2, lon2",
    [
        (20.0, 0.0, -20.0, 60.0),  # symmetric reduced latitudes
        (80.0, 0.0, 80.0, 90.0),  # high-latitude equal-latitude pair
        (10.0, 0.0, 80.0, 0.0),  # swapped: |lat1| < |lat2|, meridian
        (-21.0, -139.0, MAKKA_LAT, MAKKA_LON),  # near-antipodal, off-axis
        (0.0, -140.17, MAKKA_LAT, MAKKA_LON),  # near-antipodal, equatorial
    ],
)
def test_inverse_edge_pairs_finite(lat1, lon1, lat2, lon2):
    azi, s12 = geodesic_inverse(lat1, lon1, lat2, lon2)
    assert math.isfinite(azi) and math.isfinite(s12) and s12 >= 0


def test_inverse_seeded_sweep_invariants():
    import random

    rng = random.Random(20261003)
    for _ in range(100):
        lat1 = rng.uniform(-90, 90)
        lon1 = rng.uniform(-180, 180)
        lat2 = rng.uniform(-90, 90)
        lon2 = rng.uniform(-180, 180)
        azi12, s12 = geodesic_inverse(lat1, lon1, lat2, lon2)
        _, s21 = geodesic_inverse(lat2, lon2, lat1, lon1)
        assert math.isfinite(azi12) and math.isfinite(s12) and s12 >= 0
        assert -180 < azi12 <= 180
        assert s12 == pytest.approx(s21, rel=1e-9)
