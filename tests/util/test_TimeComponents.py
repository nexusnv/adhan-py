import math
import pytest
from datetime import datetime, timezone
from adhan.util.DateComponents import DateComponents
from adhan.util.TimeComponents import TimeComponents


@pytest.mark.parametrize(
    "value, hours, minutes, seconds",
    [
        (15.199, 15, 11, 56),
        (1.0084, 1, 0, 30),
        (1.0083, 1, 0, 29),
        (2.1, 2, 6, 0),
        (3.5, 3, 30, 0),
    ],
)
def test_from_float(value, hours, minutes, seconds):
    components = TimeComponents.from_float(value)
    assert components is not None
    assert components.hours == hours
    assert components.minutes == minutes
    assert components.seconds == seconds


def test_from_float_returns_None_when_nan_or_infinity():
    components_fron_nan = TimeComponents.from_float(math.nan)
    components_fron_inf = TimeComponents.from_float(math.inf)

    assert components_fron_nan is None
    assert components_fron_inf is None


def test_date_components():
    date = DateComponents(2015, 7, 12)

    assert TimeComponents(8, 42, 0).date_components(date) == datetime(
        2015, 7, 12, 8, 42, tzinfo=timezone.utc
    )


def test_date_components_rolls_past_midnight():
    # solar times at/after 24:00 (e.g. high-latitude sunset "24:32")
    # belong to the next day
    date = DateComponents(2015, 7, 12)

    assert TimeComponents(24, 32, 0).date_components(date) == datetime(
        2015, 7, 13, 0, 32, tzinfo=timezone.utc
    )
