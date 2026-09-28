import math
from adhan.astronomy.Astronomical import (
    approximate_transit,
    corrected_hour_angle,
    corrected_transit,
)
from adhan.astronomy.CalendricalHelper import julian_day
from adhan.data.Coordinates import Coordinates
from adhan.data.ShadowLength import ShadowLength
from adhan.astronomy.SolarCoordinates import SolarCoordinates
from adhan.util.DateComponents import DateComponents


class SolarTime:
    def __init__(self, date_components: DateComponents, coordinates: Coordinates):
        julian_date = julian_day(
            date_components.year, date_components.month, date_components.day
        )

        self.prev_solar = SolarCoordinates(julian_date - 1)
        self.solar = SolarCoordinates(julian_date)
        self.next_solar = SolarCoordinates(julian_date + 1)

        self.approximate_transit = approximate_transit(
            coordinates.longitude,
            self.solar.apparent_sidereal_time,
            self.solar.right_ascension,
        )
        solar_altitude = -50.0 / 60.0

        self.observer = coordinates
        self.transit = corrected_transit(
            self.approximate_transit,
            coordinates.longitude,
            self.solar.apparent_sidereal_time,
            self.solar.right_ascension,
            self.prev_solar.right_ascension,
            self.next_solar.right_ascension,
        )
        self.sunrise = corrected_hour_angle(
            self.approximate_transit,
            solar_altitude,
            coordinates,
            False,
            self.solar.apparent_sidereal_time,
            self.solar.right_ascension,
            self.prev_solar.right_ascension,
            self.next_solar.right_ascension,
            self.solar.declination,
            self.prev_solar.declination,
            self.next_solar.declination,
        )
        self.sunset = corrected_hour_angle(
            self.approximate_transit,
            solar_altitude,
            coordinates,
            True,
            self.solar.apparent_sidereal_time,
            self.solar.right_ascension,
            self.prev_solar.right_ascension,
            self.next_solar.right_ascension,
            self.solar.declination,
            self.prev_solar.declination,
            self.next_solar.declination,
        )

    def hour_angle(self, angle: float, after_transit: bool) -> float:
        return corrected_hour_angle(
            self.approximate_transit,
            angle,
            self.observer,
            after_transit,
            self.solar.apparent_sidereal_time,
            self.solar.right_ascension,
            self.prev_solar.right_ascension,
            self.next_solar.right_ascension,
            self.solar.declination,
            self.prev_solar.declination,
            self.next_solar.declination,
        )

    def afternoon(self, shadow_length: ShadowLength) -> float:
        # TODO (from Swift version) source shadow angle calculation
        tangent = abs(self.observer.latitude - self.solar.declination)
        inverse = shadow_length.shadow_length + math.tan(math.radians(tangent))
        angle = math.degrees(math.atan(1.0 / inverse))

        return self.hour_angle(angle, True)
