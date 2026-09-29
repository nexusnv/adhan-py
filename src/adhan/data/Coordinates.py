from dataclasses import dataclass
from decimal import Decimal
import numbers

from adhan.exceptions import ValidationError


@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        for name, value in (
            ("Latitude", self.latitude),
            ("Longitude", self.longitude),
        ):
            if isinstance(value, bool) or not isinstance(
                value, (numbers.Real, Decimal)
            ):
                raise ValidationError(f"{name} must be a real number, got {value!r}.")
        if not -90 <= self.latitude <= 90:
            raise ValidationError(
                f"Latitude must be within [-90, 90], got {self.latitude}."
            )
        if not -180 <= self.longitude <= 180:
            raise ValidationError(
                f"Longitude must be within [-180, 180], got {self.longitude}."
            )
