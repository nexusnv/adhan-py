class PrayerAdjustments:

    imsak: int
    # Imsak offset in minutes

    fajr: int
    # Fajr offset in minutes

    sunrise: int
    # Sunrise offset in minutes

    dhuhr: int
    # Dhuhr offset in minutes

    asr: int
    # Asr offset in minutes

    maghrib: int
    # Maghrib offset in minutes

    isha: int
    # Isha offset in minutes

    ishraq: int
    # Ishraq offset in minutes (applied on top of sunrise + ishraq_offset)

    dhuha: int
    # Dhuha offset in minutes (applied on top of sunrise + dhuha_offset)

    def __init__(
        self,
        fajr: int = 0,
        sunrise: int = 0,
        dhuhr: int = 0,
        asr: int = 0,
        maghrib: int = 0,
        isha: int = 0,
        imsak: int = 0,
        ishraq: int = 0,
        dhuha: int = 0,
    ):
        """
        Gets a PrayerAdjustments object to offset prayer times (defaulting to 0)
        param fajr offset from fajr in minutes
        param sunrise offset from sunrise in minutes
        param dhuhr offset from dhuhr in minutes
        param asr offset from asr in minutes
        param maghrib offset from maghrib in minutes
        param isha offset from isha in minutes
        param imsak offset from imsak in minutes
        param ishraq offset from ishraq in minutes
        param dhuha offset from dhuha in minutes
        """
        self.fajr = fajr
        self.sunrise = sunrise
        self.dhuhr = dhuhr
        self.asr = asr
        self.maghrib = maghrib
        self.isha = isha
        self.imsak = imsak
        self.ishraq = ishraq
        self.dhuha = dhuha
