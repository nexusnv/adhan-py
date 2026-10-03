from enum import Enum


class Prayer(Enum):
    """Prayer/marker identifiers in chronological definition order.

    Definition (iteration) order is the canonical chronological order:
    ``NONE, IMSAK, FAJR, SUNRISE, SYURUK, ISHRAQ, DHUHA, DHUHR, ASR,
    MAGHRIB, ISHA``. Numeric values are frozen for backward compatibility
    (``FAJR=1`` through ``ISHA=6`` predate the newer markers), so sorting
    by ``.value`` does NOT yield chronological order — iterate the enum
    itself instead.
    """

    NONE = 0

    IMSAK = 7

    FAJR = 1

    SUNRISE = 2

    SYURUK = 8

    ISHRAQ = 9

    DHUHA = 10

    DHUHR = 3

    ASR = 4

    MAGHRIB = 5

    ISHA = 6
