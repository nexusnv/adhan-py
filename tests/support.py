"""Shared test helpers.

This module is intentionally *not* named ``test_*`` so pytest does not
collect it. With no ``__init__.py`` in ``tests/``, pytest adds that
directory to ``sys.path``, making ``from support import ...`` work from
any top-level test module.
"""

from alfalak import PrayerTimes


def is_ordered(prayer_times: PrayerTimes) -> bool:
    """Monotonic invariant covering all markers.

    Only Dhuhr/Asr may coincide (documented saturation); Imsak may equal
    Fajr (offset 0) and Syuruk/Ishraq/Dhuha may coincide with sunrise and
    each other (zero offsets); every other adjacent pair is strictly
    increasing. The derived markers are checked as a sunrise-anchored chain
    (``sunrise <= syuruk <= ishraq <= dhuha``) rather than against Dhuhr, so
    very short polar-boundary days (day length under the marker offsets)
    do not read as marker disorder.
    """
    return (
        prayer_times.imsak
        <= prayer_times.fajr
        < prayer_times.sunrise
        <= prayer_times.syuruk
        <= prayer_times.ishraq
        <= prayer_times.dhuha
    ) and (
        prayer_times.sunrise
        < prayer_times.dhuhr
        <= prayer_times.asr
        < prayer_times.maghrib
        < prayer_times.isha
    )
