"""Test snow ratio calculations."""
import pytest

from custom_components.owm_precipitation_forecast.exceptions import OWMPrecipitationCalculationError
from custom_components.owm_precipitation_forecast.snow_ratio import SnowRatioCalculator


@pytest.fixture
def default_calculator():
    """Default snow ratio calculator."""
    return SnowRatioCalculator({"below_0f": 20, "0_to_15f": 15, "15_to_32f": 10, "above_32f": 0})


def test_calculate_snow_inches_below_0f(default_calculator):
    """Test snow calculation below 0°F (20:1 ratio)."""
    # 25.4mm = 1 inch liquid → 20 inches snow
    result = default_calculator.calculate_snow_inches(25.4, -5)
    assert result == pytest.approx(20.0, abs=0.01)


def test_calculate_snow_inches_0_to_15f(default_calculator):
    """Test 0-15°F range (15:1 ratio)."""
    result = default_calculator.calculate_snow_inches(25.4, 10)
    assert result == pytest.approx(15.0, abs=0.01)


def test_calculate_snow_inches_15_to_32f(default_calculator):
    """Test 15-32°F range (10:1 ratio)."""
    result = default_calculator.calculate_snow_inches(25.4, 25)
    assert result == pytest.approx(10.0, abs=0.01)


def test_no_snow_above_32f(default_calculator):
    """No snow above freezing."""
    result = default_calculator.calculate_snow_inches(25.4, 35)
    assert result == 0.0


def test_no_snow_zero_precip(default_calculator):
    """Zero precip returns zero snow."""
    result = default_calculator.calculate_snow_inches(0, 20)
    assert result == 0.0


def test_invalid_config_raises_error():
    """Invalid config raises CalculationError."""
    with pytest.raises(OWMPrecipitationCalculationError):
        SnowRatioCalculator({"missing_key": 10})
