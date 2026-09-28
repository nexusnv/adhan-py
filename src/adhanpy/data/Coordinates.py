from dataclasses import dataclass

from adhanpy.exceptions import ValidationError


@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValidationError(
                f"Latitude must be within [-90, 90], got {self.latitude}."
            )
        if not -180 <= self.longitude <= 180:
            raise ValidationError(
                f"Longitude must be within [-180, 180], got {self.longitude}."
            )
