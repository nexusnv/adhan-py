"""Shared test helpers.

This module is intentionally *not* named ``test_*`` so pytest does not
collect it. With no ``__init__.py`` in ``tests/``, pytest adds that
directory to ``sys.path``, making ``from support import ...`` work from
any top-level test module.
"""

from alfalak import PrayerTimes


def is_ordered(prayer_times: PrayerTimes) -> bool:
    """Monotonic invariant: only Dhuhr/Asr may coincide (documented
    saturation); every other adjacent pair is strictly increasing."""
    return (
        prayer_times.fajr
        < prayer_times.sunrise
        < prayer_times.dhuhr
        <= prayer_times.asr
        < prayer_times.maghrib
        < prayer_times.isha
    )
