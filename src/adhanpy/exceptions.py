class AdhanError(Exception):
    """Base class for all adhanpy errors."""


class AstronomicalError(AdhanError):
    """The sun position needed for a marker is undefined
    (polar day/night, undefined Asr)."""


class ConfigurationError(AdhanError):
    """Invalid setup (method, madhab, polar rule, prayer,
    high-latitude rule, method-vs-parameters exclusivity)."""


class ValidationError(AdhanError):
    """Out-of-range value (coordinates, angles, intervals)."""
