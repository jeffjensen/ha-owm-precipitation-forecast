"""Test precipitation calculator."""
import pytest
from datetime import datetime

from custom_components.ha_owm_precipitation_forecast.precipitation_calculator import (
    PrecipitationCalculator,
)


def test_calculate_snow_from_rain_cold() -> None:
    """Test snow calculation at cold temperatures."""
    calc = PrecipitationCalculator()

    # Test at 25°F (should use 15:1 ratio)
    snow = calc.calculate_snow_from_rain(1.0, 25.0)
    assert snow == 15.0


def test_calculate_snow_from_rain_very_cold() -> None:
    """Test snow calculation at very cold temperatures."""
    calc = PrecipitationCalculator()

    # Test at 8°F (should use 40:1 ratio)
    snow = calc.calculate_snow_from_rain(1.0, 8.0)
    assert snow == 40.0


def test_calculate_snow_from_rain_above_freezing() -> None:
    """Test snow calculation above freezing."""
    calc = PrecipitationCalculator()

    # Test at 35°F (should be 0, no snow)
    snow = calc.calculate_snow_from_rain(1.0, 35.0)
    assert snow == 0.0


def test_calculate_snow_from_rain_near_freezing() -> None:
    """Test snow calculation near freezing."""
    calc = PrecipitationCalculator()

    # Test at 30°F (should use 10:1 ratio)
    snow = calc.calculate_snow_from_rain(1.0, 30.0)
    assert snow == 10.0


def test_calculate_snow_no_rain() -> None:
    """Test snow calculation with no rain."""
    calc = PrecipitationCalculator()

    snow = calc.calculate_snow_from_rain(0.0, 25.0)
    assert snow == 0.0


def test_process_forecast_data(mock_forecast_data: dict) -> None:
    """Test processing forecast data."""
    calc = PrecipitationCalculator()
    result = calc.process_forecast_data(mock_forecast_data)

    # Check all required keys exist
    assert "hourly_rain" in result
    assert "hourly_snow" in result
    assert "daily_rain" in result
    assert "daily_snow" in result
    assert "next24h_rain" in result
    assert "next24h_snow" in result
    assert "last_update" in result

    # Check that we have data
    assert len(result["hourly_rain"]) > 0
    assert len(result["daily_rain"]) > 0

    # Check that next 24h values are calculated and positive
    assert result["next24h_rain"] > 0
    assert result["next24h_snow"] > 0


def test_process_empty_forecast(mock_empty_forecast_data: dict) -> None:
    """Test processing forecast with no precipitation."""
    calc = PrecipitationCalculator()
    result = calc.process_forecast_data(mock_empty_forecast_data)

    # Should have structure but zero values
    assert result["next24h_rain"] == 0.0
    assert result["next24h_snow"] == 0.0


def test_process_forecast_timestamps(mock_forecast_data: dict) -> None:
    """Test that timestamps are properly processed."""
    calc = PrecipitationCalculator()
    result = calc.process_forecast_data(mock_forecast_data)

    # Check first hourly entry has proper timestamp
    first_hourly = result["hourly_rain"][0]
    assert "timestamp" in first_hourly
    assert isinstance(first_hourly["timestamp"], datetime)
