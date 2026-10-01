import math
from alfalak.data.Coordinates import Coordinates
from alfalak.exceptions import ValidationError
from alfalak.util.FloatUtil import unwind_angle

MAKKAH = Coordinates(21.4225241, 39.8261818)


class Qibla:
    """
    Qibla direction for a location, in degrees clockwise from north.
    Ported from upstream adhan (adhan-kotlin Qibla/QiblaUtil).
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
