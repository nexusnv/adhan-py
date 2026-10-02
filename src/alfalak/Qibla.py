import math
from alfalak.data.Constants import EARTH_MEAN_RADIUS_KM, MAKKAH
from alfalak.data.Coordinates import Coordinates
from alfalak.exceptions import ValidationError
from alfalak.util.FloatUtil import unwind_angle

__all__ = ["MAKKAH", "Qibla"]


class Qibla:
    """
    Qibla direction and distance for a location.

    ``direction`` is degrees clockwise from north, via spherical
    trigonometry (Todhunter "Spherical Trigonometry" p.50, ported from
    upstream adhan). ``distance_to_makkah_km`` is the spherical
    great-circle distance using ``EARTH_MEAN_RADIUS_KM``.

    Spherical-Earth assumption: typically within a few arcminutes of the
    WGS84 ellipsoidal forward azimuth, worst case ~0.3-0.35 deg (NOT
    sub-0.1 deg; per published spherical-vs-ellipsoidal comparisons:
    IJRS great-circle study up to ~20 arcmin, Walisongo/Al-Hilal ~8 arcmin
    vs Vincenty). Ellipsoidal geodesics are a later slice.

    Degenerate inputs do not raise: Makkah-to-self (atan2(0, ~0),
    observed 180.0) and the true antipode (~-21.4225, -140.17, where
    every bearing is equidistant) return a float in [0, 360).
    """

    def __init__(self, coordinates: tuple[float, float] | Coordinates) -> None:
        if isinstance(coordinates, Coordinates):
            latitude = coordinates.latitude
            longitude = coordinates.longitude
        else:
            try:
                latitude, longitude = coordinates
            except (TypeError, ValueError) as e:
                raise ValidationError(
                    "Coordinates must be a (latitude, longitude) tuple or "
                    f"Coordinates, got {coordinates!r}."
                ) from e
            # Reuse Coordinates validation so non-numeric inputs raise
            # ValidationError (not bare TypeError), per the AlFalakError contract.
            validated = Coordinates(latitude, longitude)
            latitude, longitude = validated.latitude, validated.longitude

        # Equation from "Spherical Trigonometry For the use of colleges
        # and schools" page 50
        longitude_delta = math.radians(MAKKAH.longitude - longitude)
        latitude_radians = math.radians(latitude)
        term1 = math.sin(longitude_delta)
        term2 = math.cos(latitude_radians) * math.tan(math.radians(MAKKAH.latitude))
        term3 = math.sin(latitude_radians) * math.cos(longitude_delta)
        self.direction: float = unwind_angle(
            math.degrees(math.atan2(term1, term2 - term3))
        )

        # Spherical great-circle distance via the haversine atan2 form
        # (stable near 0 and antipode; naive law-of-cosines is not).
        phi1 = math.radians(latitude)
        phi2 = math.radians(MAKKAH.latitude)
        delta_phi = phi2 - phi1
        delta_lambda = math.radians(MAKKAH.longitude - longitude)
        haversine_a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        haversine_a = min(1.0, max(0.0, haversine_a))
        central_angle = 2 * math.atan2(
            math.sqrt(haversine_a), math.sqrt(1 - haversine_a)
        )
        self.distance_to_makkah_km: float = EARTH_MEAN_RADIUS_KM * central_angle
