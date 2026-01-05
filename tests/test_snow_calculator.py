"""Tests for snow calculator."""

from __future__ import annotations

import pytest

from custom_components.ha_owm_precipitation_forecast.snow_calculator import (
    SnowCalculator,
)


def test_snow_calculation_default():
    """Test basic snow calculation."""
    calc = SnowCalculator(base_ratio=10.0, use_temp_adjusted=False)

    snow = calc.calculate_snow(1.0, 0)  # 1 inch rain at 0°C

    assert snow == 10.0


def test_snow_calculation_zero():
    """Test zero precipitation."""
    calc = SnowCalculator()

    snow = calc.calculate_snow(0.0, 0)

    assert snow == 0.0


def test_temperature_adjusted_cold():
    """Test temperature-adjusted ratio for cold temps."""
    calc = SnowCalculator(base_ratio=10.0, use_temp_adjusted=True)

    snow = calc.calculate_snow(1.0, -10)  # -10°C (14°F)

    assert snow == 18.0  # 18:1 ratio for 14°F


def test_temperature_adjusted_warm():
    """Test temperature-adjusted ratio for warm temps."""
    calc = SnowCalculator(use_temp_adjusted=True)

    snow = calc.calculate_snow(1.0, 2)  # 2°C (35.6°F)

    assert snow == 0.0  # 0:1 ratio above 32°F


def test_ratio_update():
    """Test updating base ratio."""
    calc = SnowCalculator(base_ratio=10.0, use_temp_adjusted=False)

    calc.update_base_ratio(15.0)

    snow = calc.calculate_snow(1.0, 0)

    assert snow == 15.0


def test_temperature_adjusted_toggle():
    """Test toggling temperature-adjusted mode."""
    calc = SnowCalculator(base_ratio=10.0, use_temp_adjusted=True)

    calc.set_temperature_adjusted(False)

    snow = calc.calculate_snow(1.0, -15)

    assert snow == 10.0  # Uses base ratio
