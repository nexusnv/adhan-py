from datetime import datetime, timedelta


def rounded_minute(when: datetime) -> datetime:
    """
    Round a datetime to the nearest minute (half-up) and zero the
    seconds and microseconds. The carry is applied with timedelta
    arithmetic so hour/day boundaries roll over correctly
    (e.g. 10:59:31 rounds to 11:00).
    when: datetime object
    return: datetime object rounded to the nearest minute
    """
    rounded = when.replace(second=0, microsecond=0)
    if when.second >= 30:
        rounded += timedelta(minutes=1)

    return rounded
