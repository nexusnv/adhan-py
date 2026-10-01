import pytest
from alfalak.exceptions import (
    AlFalakError,
    AstronomicalError,
    ConfigurationError,
    ValidationError,
)


def test_hierarchy():
    assert issubclass(AstronomicalError, AlFalakError)
    assert issubclass(ConfigurationError, AlFalakError)
    assert issubclass(ValidationError, AlFalakError)
    assert not issubclass(AlFalakError, RuntimeError)
    assert not issubclass(AlFalakError, ValueError)


def test_catch_all_base():
    with pytest.raises(AlFalakError):
        raise AstronomicalError("polar day")
