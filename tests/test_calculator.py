"""Tests for calculator.py."""
import pytest

from custom_components.ha_owm_precipitation_forecast.calculator import (
    PrecipitationCalculator,
)
from custom_components.ha_owm_precipitation_forecast.const import DEFAULT_SNOW_RATIOS


def test_mm_to_inches():
    """Test mm to inches conversion."""
    calc = PrecipitationCalculator()

    assert round(calc.mm_to_inches(25.4), 2) == 1.0
    assert round(calc.mm_to_inches(10), 2) == 0.39
    assert round(calc.mm_to_inches(50.8), 2) == 2.0
    assert calc.mm_to_inches(0) == 0.0
    assert calc.mm_to_inches(1) > 0


def test_inches_to_cm():
    """Test inches to cm conversion."""
    calc = PrecipitationCalculator()

    assert calc.inches_to_cm(1.0) == 2.54
    assert calc.inches_to_cm(10.0) == 25.4
    assert calc.inches_to_cm(2.5) == 6.35
    assert calc.inches_to_cm(0) == 0.0


def test_get_snow_ratio_below_15():
    """Test snow ratio for very cold temps."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(10.0) == 20.0
    assert calc.get_snow_ratio(0.0) == 20.0
    assert calc.get_snow_ratio(-5.0) == 20.0
    assert calc.get_snow_ratio(14.9) == 20.0


def test_get_snow_ratio_15_to_20():
    """Test snow ratio for 15-20°F."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(15.0) == 18.0
    assert calc.get_snow_ratio(17.5) == 18.0
    assert calc.get_snow_ratio(19.5) == 18.0
    assert calc.get_snow_ratio(19.9) == 18.0


def test_get_snow_ratio_20_to_25():
    """Test snow ratio for 20-25°F."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(20.0) == 15.0
    assert calc.get_snow_ratio(22.0) == 15.0
    assert calc.get_snow_ratio(24.5) == 15.0
    assert calc.get_snow_ratio(24.9) == 15.0


def test_get_snow_ratio_25_to_30():
    """Test snow ratio for 25-30°F."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(25.0) == 12.0
    assert calc.get_snow_ratio(27.0) == 12.0
    assert calc.get_snow_ratio(28.0) == 12.0
    assert calc.get_snow_ratio(29.9) == 12.0


def test_get_snow_ratio_30_to_32():
    """Test snow ratio for 30-32°F."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(30.0) == 10.0
    assert calc.get_snow_ratio(31.0) == 10.0
    assert calc.get_snow_ratio(31.5) == 10.0
    assert calc.get_snow_ratio(31.9) == 10.0


def test_get_snow_ratio_above_32():
    """Test snow ratio above freezing."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(32.0) == 0.0
    assert calc.get_snow_ratio(33.0) == 0.0
    assert calc.get_snow_ratio(40.0) == 0.0
    assert calc.get_snow_ratio(50.0) == 0.0
    assert calc.get_snow_ratio(100.0) == 0.0


def test_mm_to_snow_inches_cold():
    """Test snow calculation for cold temperatures."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(10.0, 10.0)
    assert 7.8 < result < 7.9


def test_mm_to_snow_inches_moderate():
    """Test snow calculation for moderate temperatures."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(10.0, 22.0)
    assert 5.9 < result < 6.0


def test_mm_to_snow_inches_warm():
    """Test snow calculation for warm temperatures."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(10.0, 31.0)
    assert 3.9 < result < 4.0


def test_mm_to_snow_inches_above_freezing():
    """Test snow calculation above freezing (should be 0)."""
    calc = PrecipitationCalculator()

    assert calc.mm_to_snow_inches(10.0, 35.0) == 0.0
    assert calc.mm_to_snow_inches(100.0, 40.0) == 0.0
    assert calc.mm_to_snow_inches(5.0, 50.0) == 0.0


def test_mm_to_snow_inches_zero_precip():
    """Test snow calculation with zero precipitation."""
    calc = PrecipitationCalculator()

    assert calc.mm_to_snow_inches(0.0, 10.0) == 0.0
    assert calc.mm_to_snow_inches(0.0, 20.0) == 0.0
    assert calc.mm_to_snow_inches(0.0, 30.0) == 0.0


def test_custom_snow_ratios():
    """Test custom snow ratios."""
    custom_ratios = {
        "below_15": 25.0,
        "15_to_20": 22.0,
        "20_to_25": 18.0,
        "25_to_30": 15.0,
        "30_to_32": 12.0,
        "above_32": 0.0,
    }
    calc = PrecipitationCalculator(custom_ratios)

    assert calc.get_snow_ratio(10.0) == 25.0
    assert calc.get_snow_ratio(16.0) == 22.0
    assert calc.get_snow_ratio(22.0) == 18.0
    assert calc.get_snow_ratio(28.0) == 15.0
    assert calc.get_snow_ratio(31.0) == 12.0
    assert calc.get_snow_ratio(35.0) == 0.0


def test_snow_calculation_real_world_scenario():
    """Test realistic snow accumulation scenario."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(25.0, 25.0)
    assert 11.7 < result < 11.9


def test_snow_calculation_heavy_storm():
    """Test heavy snowstorm calculation."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(50.0, 15.0)
    assert 35.0 < result < 36.0


def test_snow_calculation_light_flurries():
    """Test light snow calculation."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(1.0, 20.0)
    assert 0.5 < result < 0.6


def test_calculator_initialization_with_defaults():
    """Test calculator initializes with default ratios."""
    calc = PrecipitationCalculator()

    assert calc.snow_ratios == DEFAULT_SNOW_RATIOS


def test_calculator_initialization_with_custom():
    """Test calculator initializes with custom ratios."""
    custom = {"below_15": 30.0}
    calc = PrecipitationCalculator(custom)

    assert calc.snow_ratios == custom


def test_snow_ratio_boundary_conditions():
    """Test snow ratios at exact boundary temperatures."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(15.0) == 18.0
    assert calc.get_snow_ratio(20.0) == 15.0
    assert calc.get_snow_ratio(25.0) == 12.0
    assert calc.get_snow_ratio(30.0) == 10.0
    assert calc.get_snow_ratio(32.0) == 0.0


def test_negative_temperature_handling():
    """Test handling of negative temperatures."""
    calc = PrecipitationCalculator()

    assert calc.get_snow_ratio(-20.0) == 20.0
    assert calc.get_snow_ratio(-40.0) == 20.0

    result = calc.mm_to_snow_inches(10.0, -10.0)
    assert result > 0


def test_extreme_precipitation_values():
    """Test extreme precipitation amounts."""
    calc = PrecipitationCalculator()

    result = calc.mm_to_snow_inches(100.0, 20.0)
    assert result > 50

    result = calc.mm_to_snow_inches(0.1, 20.0)
    assert 0 < result < 0.1


def test_conversion_precision():
    """Test precision of conversions."""
    calc = PrecipitationCalculator()

    mm_value = 12.7
    inches = calc.mm_to_inches(mm_value)
    assert abs(inches - 0.5) < 0.01

    cm_value = calc.inches_to_cm(inches)
    assert abs(cm_value - (mm_value / 10)) < 0.01
