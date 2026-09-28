from enum import Enum


class PolarCircleRule(Enum):

    NONE = 0
    """
    No polar fallback: raise AstronomicalError when the sun never rises
    or sets (polar day/night), as before.
    """

    NEAREST_LATITUDE = 1
    """
    Aqrab al-Bilad: compute times at the nearest latitude (same
    longitude and date) where the sun still rises and sets.
    This is the default.
    """

    NEAREST_DAY = 2
    """
    Aqrab al-Ayyam: use the schedule of the nearest date (same
    location) on which the sun rises and sets. Returned datetimes
    carry that date.
    """

    MAKKAH = 3
    """
    Follow Makkah time: compute the schedule for Makkah's
    coordinates on the same date.
    """
