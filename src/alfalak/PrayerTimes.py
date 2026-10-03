from __future__ import annotations
import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo
from alfalak.calculation.CalculationMethod import CalculationMethod
from alfalak.calculation.CalculationParameters import CalculationParameters
from alfalak.calculation.Madhab import Madhab
from alfalak.calculation.PolarCircleRule import PolarCircleRule
from alfalak.calculation.PrayerAdjustments import PrayerAdjustments
from alfalak.exceptions import AstronomicalError, ConfigurationError, ValidationError
from alfalak.calculation.Twilight import (
    season_adjusted_evening_twilight,
    season_adjusted_morning_twilight,
)
from alfalak.astronomy.SolarTime import SolarTime
from alfalak.data.Coordinates import Coordinates
from alfalak.data.Prayer import Prayer
from alfalak.Qibla import MAKKAH
from alfalak.util.TimeComponents import TimeComponents
from alfalak.util.DateComponents import DateComponents
from alfalak.util.CalendarUtil import rounded_minute


def _schedule_defined(
    date_components: DateComponents, coordinates: Coordinates
) -> bool:
    # Exactly what PrayerTimes.__init__ needs: today's sunrise/sunset plus
    # tomorrow's sunrise (for the night length). Both days are probed
    # because validity can differ across midnight at the razor edge.
    today = SolarTime(date_components, coordinates)
    if math.isnan(today.sunrise) or math.isnan(today.sunset):
        return False
    base = datetime(
        date_components.year,
        date_components.month,
        date_components.day,
        tzinfo=timezone.utc,
    )
    tomorrow = SolarTime(DateComponents.from_utc(base + timedelta(days=1)), coordinates)
    return not math.isnan(tomorrow.sunrise)


def _nearest_latitude_with_sunrise_sunset(
    latitude: float, longitude: float, date_components: DateComponents
) -> float:
    # Rise/set existence is monotonic in |latitude| for a fixed date, so
    # bisect between the (invalid) requested latitude and the equator,
    # where the sun always rises and sets.
    sign = 1.0 if latitude >= 0 else -1.0
    invalid, valid = abs(latitude), 0.0
    for _ in range(60):
        mid = (invalid + valid) / 2
        if _schedule_defined(date_components, Coordinates(sign * mid, longitude)):
            valid = mid
        else:
            invalid = mid
    # Back off toward the equator: exactly at the boundary the sun only
    # grazes the horizon (minutes-long night), where the night-fraction
    # caps for Fajr/Isha invert. Half a degree keeps the estimate nearest
    # while restoring a usable day/night split.
    return sign * max(valid - 0.5, 0.0)


def _nearest_date_with_sunrise_sunset(
    latitude: float, longitude: float, date_components: DateComponents
) -> DateComponents:
    coordinates = Coordinates(latitude, longitude)
    base = datetime(
        date_components.year,
        date_components.month,
        date_components.day,
        tzinfo=timezone.utc,
    )
    for offset in range(1, 367):
        for delta in (-offset, offset):
            candidate = DateComponents.from_utc(base + timedelta(days=delta))
            if _schedule_defined(candidate, coordinates):
                return candidate
    raise AstronomicalError(  # pragma: no cover - every location has rise/set days
        "No date with sunrise/sunset found within a year. "
        "At the exact geographic poles (|latitude| == 90) the sun's "
        "hour-angle is singular and no such date exists numerically; "
        "use PolarCircleRule.NEAREST_LATITUDE or MAKKAH instead."
    )


class PrayerTimes:
    imsak: datetime
    fajr: datetime
    sunrise: datetime
    dhuhr: datetime
    asr: datetime
    maghrib: datetime
    isha: datetime

    def __init__(
        self,
        coordinates: tuple[float, float] | Coordinates,
        date: datetime | DateComponents,
        calculation_method: Optional[CalculationMethod] = None,
        calculation_parameters: Optional[CalculationParameters] = None,
        time_zone: Optional[ZoneInfo] = None,
    ):
        """
        Arguments:
            coordinates: (latitude, longitude) tuple or Coordinates
            date: datetime or DateComponents (only the calendar date is used)
            calculation_parameters: CalculationParameters
            time_zone: example ZoneInfo("Europe/London")
        Returns:
            PrayerTimes object with UTC datetimes for imsak, fajr, sunrise, dhuhr, asr, maghrib and isha
        """

        if (calculation_parameters is None) == (calculation_method is None):
            raise ConfigurationError(
                "Only one of calculation_method or calculation_parameters must be passed."
            )

        if calculation_parameters is None:
            calculation_parameters = CalculationParameters(method=calculation_method)

        self.calculation_parameters = calculation_parameters

        if isinstance(coordinates, Coordinates):
            self.coordinates = coordinates
        else:
            try:
                latitude, longitude = coordinates
            except (TypeError, ValueError) as e:
                raise ValidationError(
                    "Coordinates must be a (latitude, longitude) tuple or "
                    f"Coordinates, got {coordinates!r}."
                ) from e
            self.coordinates = Coordinates(latitude, longitude)
        self._date_components = DateComponents.from_utc(date)
        self.time_zone = time_zone

        self._resolve_polar_circle()

        self._prayer_date = datetime(
            self._date_components.year,
            self._date_components.month,
            self._date_components.day,
            tzinfo=timezone.utc,
        )

        self._day_of_year = self._prayer_date.timetuple().tm_yday

        tomorrow_date = self._prayer_date + timedelta(days=1)
        tomorrow_date_components = DateComponents.from_utc(tomorrow_date)

        self._solar_time = SolarTime(self._date_components, self.coordinates)

        time_components = TimeComponents.from_float(self._solar_time.transit)
        transit = (
            None
            if time_components is None
            else time_components.date_components(self._date_components)
        )

        time_components = TimeComponents.from_float(self._solar_time.sunrise)
        sunrise_components = (
            None
            if time_components is None
            else time_components.date_components(self._date_components)
        )

        time_components = TimeComponents.from_float(self._solar_time.sunset)
        sunset_components = (
            None
            if time_components is None
            else time_components.date_components(self._date_components)
        )

        tomorrow_solar_time = SolarTime(tomorrow_date_components, self.coordinates)
        tomorrow_sunrise_components = TimeComponents.from_float(
            tomorrow_solar_time.sunrise
        )

        if (
            transit is None
            or sunrise_components is None
            or sunset_components is None
            or tomorrow_sunrise_components is None
        ):
            raise AstronomicalError(
                "Unable to compute prayer times: sunrise, sunset, or solar "
                "transit is undefined for these coordinates and date "
                "(polar day/night). "
                f"coordinates={self.coordinates}, "
                f"date={self._date_components}."
            )

        # All components are datetime from here on: the guard above raised
        # if any of them was None.
        self._sunrise_components: datetime = sunrise_components
        self._sunset_components: datetime = sunset_components

        # get night length
        tomorrow_sunrise = tomorrow_sunrise_components.date_components(
            tomorrow_date_components
        )
        self.night_length = (
            tomorrow_sunrise.timestamp() * 1000
            - self._sunset_components.timestamp() * 1000
        )
        self.night_portions = self.calculation_parameters.night_portions()

        # Assign final times to properties with all offsets
        self._set_fajr()
        self._set_imsak()
        self._set_sunrise()
        self._set_dhuhr(transit)
        self._set_asr()
        self._set_maghrib()
        if self.asr > self.maghrib:
            # Near the polar boundary the shadow-length hour angle can spill
            # past sunset (Asr lands after Maghrib); Asr cannot follow
            # Maghrib. Mirrors the Asr<Dhuhr saturation in _set_asr.
            self.asr = self.maghrib
        self._set_isha(self._sunset_components)

        self._adjust_prayers_time_zone()

    def _resolve_polar_circle(self) -> None:
        """
        Estimate coordinates/date when the sun never rises or sets, per
        the configured PolarCircleRule. No-op for normal days.
        """
        rule = self.calculation_parameters.polar_circle_rule
        if _schedule_defined(self._date_components, self.coordinates):
            return

        if rule == PolarCircleRule.NONE:
            return
        elif rule == PolarCircleRule.NEAREST_LATITUDE:
            self.coordinates = Coordinates(
                _nearest_latitude_with_sunrise_sunset(
                    self.coordinates.latitude,
                    self.coordinates.longitude,
                    self._date_components,
                ),
                self.coordinates.longitude,
            )
        elif rule == PolarCircleRule.NEAREST_DAY:
            self._date_components = _nearest_date_with_sunrise_sunset(
                self.coordinates.latitude,
                self.coordinates.longitude,
                self._date_components,
            )
        elif rule == PolarCircleRule.MAKKAH:
            self.coordinates = Coordinates(MAKKAH.latitude, MAKKAH.longitude)
        else:
            raise ConfigurationError(f"Unknown polar circle rule: {rule!r}.")

    def _set_fajr(self) -> None:
        temp_fajr = None
        if time_components := TimeComponents.from_float(
            self._solar_time.hour_angle(-self.calculation_parameters.fajr_angle, False)
        ):
            temp_fajr = time_components.date_components(self._date_components)

        if (
            self.calculation_parameters.method
            == CalculationMethod.MOON_SIGHTING_COMMITTEE
        ):
            if self.coordinates.latitude >= 55:
                temp_fajr = self._sunrise_components + timedelta(
                    seconds=-1 * int(self.night_length / 7000)
                )

            safe_fajr = season_adjusted_morning_twilight(
                self.coordinates.latitude,
                self._day_of_year,
                self._prayer_date.year,
                self._sunrise_components,
            )
        else:
            portion = self.night_portions.fajr
            night_fraction = int(portion * self.night_length / 1000)
            safe_fajr = self._sunrise_components + timedelta(
                seconds=-1 * night_fraction
            )

        if temp_fajr is None or temp_fajr < safe_fajr:
            temp_fajr = safe_fajr

        self.fajr = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "fajr",
            temp_fajr,
        )

    def _set_imsak(self) -> None:
        # Imsak tracks the rounded Fajr (fajr adjustments flow through),
        # minus the configurable offset. Integer-minute offsets commute with
        # half-up minute rounding, so pre/post-rounding order is equivalent;
        # imsak-specific adjustments apply on top via _rounded_minute.
        self.imsak = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "imsak",
            self.fajr - timedelta(minutes=self.calculation_parameters.imsak_offset),
        )

    def _set_sunrise(self) -> None:
        self.sunrise = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "sunrise",
            self._sunrise_components,
        )

    def _set_dhuhr(self, time: datetime) -> None:
        self.dhuhr = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "dhuhr",
            time,
        )

    def _set_asr(self) -> None:
        madhab = self.calculation_parameters.madhab
        if not isinstance(madhab, Madhab):
            raise ConfigurationError(f"Unknown madhab: {madhab!r}.")

        temp_asr = None
        if time_components := TimeComponents.from_float(
            self._solar_time.afternoon(madhab.get_shadow_length())
        ):
            temp_asr = time_components.date_components(self._date_components)

        if temp_asr is None:
            raise AstronomicalError(
                "Unable to compute Asr: the afternoon shadow length is "
                "undefined for these coordinates and date "
                f"(coordinates={self.coordinates}, "
                f"date={self._date_components})."
            )

        self.asr = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "asr",
            temp_asr,
        )

        if self.asr < self.dhuhr:
            # Near the polar boundary the sun may never reach the shadow
            # altitude and the hour-angle math lands before transit; Asr
            # cannot precede Dhuhr (also covers dhuhr-only adjustments
            # and rounding splits).
            self.asr = self.dhuhr

    def _set_maghrib(self) -> None:
        self.maghrib = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "maghrib",
            self._sunset_components,
        )

    def _set_isha(self, sunset: datetime) -> None:
        # Isha calculation with check against safe value
        temp_isha = None
        try:
            # NOTE: stays ValueError on purpose - the except (ValueError,
            # TypeError) below depends on this exact type to switch to
            # angle-based Isha. Not part of the public error tree.
            if self.calculation_parameters.isha_interval < 1:
                raise ValueError("Isha interval is either not defined or less than 1.")

            temp_isha = sunset + timedelta(
                seconds=self.calculation_parameters.isha_interval * 60
            )
        except (ValueError, TypeError):
            timeComponents = TimeComponents.from_float(
                self._solar_time.hour_angle(
                    -self.calculation_parameters.isha_angle, True
                )
            )

            if timeComponents is not None:
                temp_isha = timeComponents.date_components(self._date_components)

            if (
                self.calculation_parameters.method
                == CalculationMethod.MOON_SIGHTING_COMMITTEE
                and self.coordinates.latitude >= 55
            ):
                night_fraction = int(self.night_length / 7000)
                temp_isha = self._sunset_components + timedelta(seconds=night_fraction)

            if (
                self.calculation_parameters.method
                == CalculationMethod.MOON_SIGHTING_COMMITTEE
            ):
                safe_isha = season_adjusted_evening_twilight(
                    self.coordinates.latitude,
                    self._day_of_year,
                    self._date_components.year,
                    self._sunset_components,
                )
            else:
                portion = self.night_portions.isha
                night_fraction = int(portion * self.night_length / 1000)

                safe_isha = self._sunset_components + timedelta(
                    seconds=int(night_fraction)
                )

            if temp_isha is None or temp_isha > safe_isha:
                temp_isha = safe_isha

        self.isha = self._rounded_minute(
            self.calculation_parameters.adjustments,
            self.calculation_parameters.method_adjustments,
            "isha",
            temp_isha,
        )

    def _rounded_minute(
        self,
        adjustments: PrayerAdjustments,
        method_adjustments: PrayerAdjustments,
        prayer_name: str,
        temp_prayer: datetime,
    ) -> datetime:
        prayer_adjustments = getattr(adjustments, prayer_name)
        method_prayer_adjustments = getattr(method_adjustments, prayer_name)
        return rounded_minute(
            (temp_prayer + timedelta(minutes=prayer_adjustments))
            + timedelta(minutes=method_prayer_adjustments)
        )

    def time_for_prayer(self, prayer: Prayer) -> datetime:
        """Return the computed time for a Prayer enum member."""
        if prayer == Prayer.IMSAK:
            return self.imsak
        elif prayer == Prayer.FAJR:
            return self.fajr
        elif prayer == Prayer.SUNRISE:
            return self.sunrise
        elif prayer == Prayer.DHUHR:
            return self.dhuhr
        elif prayer == Prayer.ASR:
            return self.asr
        elif prayer == Prayer.MAGHRIB:
            return self.maghrib
        elif prayer == Prayer.ISHA:
            return self.isha
        raise ConfigurationError(f"Unknown prayer: {prayer!r}.")

    def _adjust_prayers_time_zone(self) -> None:
        if self.time_zone is not None:
            self.imsak = self.imsak.astimezone(self.time_zone)
            self.fajr = self.fajr.astimezone(self.time_zone)
            self.sunrise = self.sunrise.astimezone(self.time_zone)
            self.dhuhr = self.dhuhr.astimezone(self.time_zone)
            self.asr = self.asr.astimezone(self.time_zone)
            self.maghrib = self.maghrib.astimezone(self.time_zone)
            self.isha = self.isha.astimezone(self.time_zone)
