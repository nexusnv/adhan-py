import pytest
from adhanpy.exceptions import (
    AdhanError,
    AstronomicalError,
    ConfigurationError,
    ValidationError,
)


def test_hierarchy():
    assert issubclass(AstronomicalError, AdhanError)
    assert issubclass(ConfigurationError, AdhanError)
    assert issubclass(ValidationError, AdhanError)
    assert not issubclass(AdhanError, RuntimeError)
    assert not issubclass(AdhanError, ValueError)


def test_catch_all_base():
    with pytest.raises(AdhanError):
        raise AstronomicalError("polar day")
