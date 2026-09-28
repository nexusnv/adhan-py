from datetime import datetime, timezone
import pytest
import adhan.util.CalendarUtil as CalendarUtil


def test_rounding_when_second_is_less_than_30():
    dt = datetime(2015, 1, 1, 10, 2, 29, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert rounded.minute == 2
    assert rounded.second == 0


def test_rounding_when_second_is_greater_than_30():
    dt = datetime(2015, 1, 1, 10, 2, 31)
    rounded = CalendarUtil.rounded_minute(dt)

    assert rounded.minute == 3
    assert rounded.second == 0


def test_rounding_when_second_is_greater_than_30_and_minute_is_59_rolls_hour():
    dt = datetime(2015, 1, 1, 10, 59, 31, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert rounded.hour == 11
    assert rounded.minute == 0
    assert rounded.second == 0


@pytest.mark.parametrize(
    "second, expected_minute",
    [(0, 2), (29, 2), (31, 3)],
)
def test_rounding_boundaries(second, expected_minute):
    dt = datetime(2015, 1, 1, 10, 2, second, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert (rounded.hour, rounded.minute, rounded.second) == (
        10,
        expected_minute,
        0,
    )


def test_rounding_carries_into_next_hour():
    dt = datetime(2015, 1, 1, 10, 59, 31, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert (rounded.hour, rounded.minute, rounded.second) == (11, 0, 0)


def test_rounding_half_up_at_exactly_30_seconds():
    dt = datetime(2015, 1, 1, 10, 2, 30, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert (rounded.hour, rounded.minute) == (10, 3)


def test_rounding_zeroes_microseconds_without_carry():
    # 29.9s is nearest to 10:02 (microseconds cannot flip a half-up
    # decision since `second` is integral); only the retained
    # microseconds are wrong here
    dt = datetime(2015, 1, 1, 10, 2, 29, 900000, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert rounded == datetime(2015, 1, 1, 10, 2, 0, tzinfo=timezone.utc)


def test_rounding_zeroes_microseconds_with_carry():
    dt = datetime(2015, 1, 1, 10, 2, 59, 999999, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert rounded == datetime(2015, 1, 1, 10, 3, 0, tzinfo=timezone.utc)


def test_rounding_zeroes_microseconds():
    dt = datetime(2015, 1, 1, 10, 2, 10, 500000, tzinfo=timezone.utc)
    rounded = CalendarUtil.rounded_minute(dt)

    assert rounded == datetime(2015, 1, 1, 10, 2, 0, tzinfo=timezone.utc)
