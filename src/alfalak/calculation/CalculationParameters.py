import copy
import math
from typing import Optional
from alfalak.calculation.CalculationMethod import CalculationMethod
from alfalak.calculation.MethodsParameters import METHODS_PARAMETERS
from alfalak.calculation.Madhab import Madhab
from alfalak.calculation.HighLatitudeRule import HighLatitudeRule
from alfalak.calculation.PolarCircleRule import PolarCircleRule
from alfalak.calculation.PrayerAdjustments import PrayerAdjustments
from alfalak.data.NightPortions import NightPortions
from alfalak.exceptions import ConfigurationError, ValidationError


class CalculationParameters:
    def __init__(
        self,
        method: Optional[CalculationMethod] = None,
        adjustments: Optional[PrayerAdjustments] = None,
        method_adjustments: Optional[PrayerAdjustments] = None,
        isha_interval: int = 0,
        fajr_angle: float = 0.0,
        isha_angle: float = 0.0,
        polar_circle_rule: PolarCircleRule = PolarCircleRule.NEAREST_LATITUDE,
        imsak_offset: int = 10,
        ishraq_offset: int = 15,
        dhuha_offset: int = 28,
        elevation_m: float = 0.0,
        is_ramadan: bool = False,
    ) -> None:
        # The madhab used to calculate Asr
        self.madhab = Madhab.SHAFI

        # Rules for placing bounds on Fajr and Isha for high latitude areas
        self.high_latitude_rule = HighLatitudeRule.MIDDLE_OF_THE_NIGHT

        # Minutes after Maghrib (if set, the time for Isha will be Maghrib plus isha_interval)
        self.isha_interval = isha_interval

        # fajr and isha angles
        self.fajr_angle = fajr_angle
        self.isha_angle = isha_angle

        # Minutes before Fajr for Imsak (JAKIM convention defaults to 10;
        # published tables are mostly but not always exactly Fajr-10, so
        # this stays configurable rather than hardcoded)
        self.imsak_offset = imsak_offset

        # Observer eye height in metres for dip-of-horizon correction
        # (h0 = −0.833° − 0.0293°·√h_m). Default 0 = sea level, unchanged.
        self.elevation_m = elevation_m

        # Minutes after sunrise for Ishraq (15 per Ibn Uthaymin) and for the
        # start of the Dhuha window (28 per a single Malaysian Syuruk+28
        # source, not universal fiqh — configurable, see docs)
        self.ishraq_offset = ishraq_offset
        self.dhuha_offset = dhuha_offset

        # Umm al-Qura Ramadan mode: Isha is 120 minutes after Maghrib in
        # Ramadan vs 90 otherwise (total, not an additive +30). Opt-in flag;
        # applies to the UMM_AL_QURA preset only.
        self.is_ramadan = is_ramadan

        # Estimation strategy when the sun never rises/sets (polar day/night)
        if not isinstance(polar_circle_rule, PolarCircleRule):
            raise ConfigurationError(
                "polar_circle_rule must be a PolarCircleRule, "
                f"got {type(polar_circle_rule).__name__}."
            )
        self.polar_circle_rule = polar_circle_rule

        # Used to optionally add or subtract a set amount of time from each prayer time
        # (copied: a caller-provided object is never aliased into the instance)
        self.adjustments = (
            copy.copy(adjustments) if adjustments is not None else PrayerAdjustments()
        )

        # method is last assigned and has precedence and will overwrite other parameters
        if method is None:
            self.method = CalculationMethod.NONE
        elif isinstance(method, CalculationMethod):
            self.method = method
        else:
            raise ConfigurationError(
                "method must be a CalculationMethod or None, "
                f"got {type(method).__name__}."
            )

        # Used for method adjustments (copied for the same reason)
        self.method_adjustments = (
            copy.copy(method_adjustments)
            if method_adjustments is not None
            else PrayerAdjustments()
        )

        self._set_parameters_using_method()

        if not 0 <= self.fajr_angle <= 90:
            raise ValidationError(
                f"Fajr angle must be within [0, 90], got {self.fajr_angle}."
            )
        if not 0 <= self.isha_angle <= 90:
            raise ValidationError(
                f"Isha angle must be within [0, 90], got {self.isha_angle}."
            )
        if self.isha_interval < 0:
            raise ValidationError(
                f"Isha interval must be non-negative, got {self.isha_interval}."
            )
        if self.imsak_offset < 0:
            raise ValidationError(
                f"Imsak offset must be non-negative, got {self.imsak_offset}."
            )
        if self.ishraq_offset < 0:
            raise ValidationError(
                f"Ishraq offset must be non-negative, got {self.ishraq_offset}."
            )
        if self.dhuha_offset < 0:
            raise ValidationError(
                f"Dhuha offset must be non-negative, got {self.dhuha_offset}."
            )
        if (
            isinstance(self.elevation_m, bool)
            or not isinstance(self.elevation_m, (int, float))
            or not math.isfinite(self.elevation_m)
            or self.elevation_m < 0
        ):
            raise ValidationError(
                "Elevation must be a finite non-negative number of metres, "
                f"got {self.elevation_m!r}."
            )

    def night_portions(self) -> NightPortions:
        if self.high_latitude_rule == HighLatitudeRule.MIDDLE_OF_THE_NIGHT:
            return NightPortions(1.0 / 2.0, 1.0 / 2.0)

        elif self.high_latitude_rule == HighLatitudeRule.SEVENTH_OF_THE_NIGHT:
            return NightPortions(1.0 / 7.0, 1.0 / 7.0)

        elif self.high_latitude_rule == HighLatitudeRule.TWILIGHT_ANGLE:
            return NightPortions(self.fajr_angle / 60.0, self.isha_angle / 60.0)

        raise ConfigurationError("Invalid high latitude rule")

    def _set_parameters_using_method(self) -> None:
        method_parameters = METHODS_PARAMETERS[self.method]
        for key, value in method_parameters.items():
            # Copy: METHODS_PARAMETERS holds shared template objects and
            # must never be aliased into (and mutated through) instances.
            setattr(self, key, copy.copy(value))
