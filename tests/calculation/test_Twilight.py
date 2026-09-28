from datetime import datetime, timedelta, timezone
import pytest
from adhan.calculation.Twilight import (
    days_since_solstice,
    season_adjusted_evening_twilight,
    season_adjusted_morning_twilight,
)


@pytest.mark.parametrize(
    "year, month, day, latitude, expected",
    [
        (2016, 1, 1, 1, 11),
        (2015, 12, 31, 1, 10),
        (2016, 12, 31, 1, 10),
        (2016, 12, 21, 1, 0),
        (2016, 12, 22, 1, 1),
        (2016, 3, 1, 1, 71),
        (2015, 3, 1, 1, 70),
        (2016, 12, 20, 1, 365),
        (2015, 12, 20, 1, 364),
        (2015, 6, 21, -1, 0),
        (2016, 6, 21, -1, 0),
        (2015, 6, 20, -1, 364),
        (2016, 6, 20, -1, 365),
    ],
)
def test_days_since_solstice(year, month, day, latitude, expected):
    """
    For Northern Hemisphere start from December 21
    (DYY=0 for December 21, and counting forward, DYY=11 for January 1 and so on).
    For Southern Hemisphere start from June 21
    (DYY=0 for June 21, and counting forward)
    """

    # Arrange
    date = datetime(year, month, day)
    day_of_year = date.timetuple().tm_yday

    # Act, Assert
    assert days_since_solstice(day_of_year, date.year, latitude) == expected


def test_season_adjusted_twilight_ordering_and_ranges():
    # morning twilight precedes sunrise, evening twilight follows sunset, and
    # the seasonal adjustment stays within its physical band across
    # latitudes, seasons, and leap/non-leap years
    sunrise = datetime(2015, 7, 12, 10, 8, tzinfo=timezone.utc)
    sunset = datetime(2015, 7, 12, 17, 20, tzinfo=timezone.utc)

    for latitude in [0.0, 23.5, 35.77, 51.5, 59.9, 66.5, -33.8, -54.0]:
        for day_of_year, year in [
            (1, 2016),
            (80, 2015),
            (172, 2015),
            (266, 2015),
            (355, 2015),
        ]:
            morning = season_adjusted_morning_twilight(
                latitude, day_of_year, year, sunrise
            )
            evening = season_adjusted_evening_twilight(
                latitude, day_of_year, year, sunset
            )

            assert morning < sunrise
            assert evening > sunset
            assert 70 <= (sunrise - morning).total_seconds() / 60 <= 140
            assert 70 <= (evening - sunset).total_seconds() / 60 <= 110


def test_season_adjusted_twilight_equator_exact_values():
    # at the equator the adjustment curve is flat at 75 minutes
    sunrise = datetime(2015, 3, 21, 10, 8, tzinfo=timezone.utc)
    sunset = datetime(2015, 3, 21, 17, 20, tzinfo=timezone.utc)

    assert season_adjusted_morning_twilight(
        0.0, 80, 2015, sunrise
    ) == sunrise - timedelta(minutes=75)
    assert season_adjusted_evening_twilight(
        0.0, 80, 2015, sunset
    ) == sunset + timedelta(minutes=75)
