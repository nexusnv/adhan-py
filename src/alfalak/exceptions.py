class AlFalakError(Exception):
    """Base class for all al-falak errors."""


class AstronomicalError(AlFalakError):
    """The sun position needed for a marker is undefined
    (polar day/night, undefined Asr)."""


class ConfigurationError(AlFalakError):
    """Invalid setup (method, madhab, polar rule, prayer,
    high-latitude rule, method-vs-parameters exclusivity)."""


class ValidationError(AlFalakError):
    """Out-of-range value (coordinates, angles, intervals)."""
