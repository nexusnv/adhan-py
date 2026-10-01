import pytest
from alfalak.calculation.Madhab import Madhab
from alfalak.exceptions import ConfigurationError


def test_shafi_shadow_length():
    assert Madhab.SHAFI.get_shadow_length().shadow_length == pytest.approx(1.0)


def test_hanafi_shadow_length():
    assert Madhab.HANAFI.get_shadow_length().shadow_length == pytest.approx(2.0)


def test_unknown_madhab_raises():
    with pytest.raises(ConfigurationError, match="(?i)madhab"):
        Madhab.get_shadow_length(None)
