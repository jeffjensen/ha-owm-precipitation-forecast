"""Tests for sensor.py."""
import pytest
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT

from custom_components.ha_owm_precipitation_forecast.const import (
    DOMAIN,
    ENTITY_PREFIX,
    UNIT_INCHES,
)


@pytest.mark.asyncio
async def test_sensor_setup(hass: HomeAssistant, mock_config_entry, mock_owm_client):
    """Test sensor setup."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Check rain sensors
        rain_next24h = hass.states.get(
            f"sensor.{ENTITY_PREFIX}_test_location_rain_next24h"
        )
        assert rain_next24h is not None
        assert rain_next24h.attributes[ATTR_UNIT_OF_MEASUREMENT] == UNIT_INCHES

        # Check snow sensors
        snow_next24h = hass.states.get(
            f"sensor.{ENTITY_PREFIX}_test_location_snow_next24h"
        )
        assert snow_next24h is not None
        assert snow_next24h.attributes[ATTR_UNIT_OF_MEASUREMENT] == UNIT_INCHES


@pytest.mark.asyncio
async def test_sensor_values(hass: HomeAssistant, mock_config_entry, mock_owm_client):
    """Test sensor values are calculated correctly."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        snow_sensor = hass.states.get(
            f"sensor.{ENTITY_PREFIX}_test_location_snow_next24h"
        )
        assert snow_sensor is not None

        # Value should be > 0 due to mock data
        assert float(snow_sensor.state) > 0


@pytest.mark.asyncio
async def test_sensor_attributes(hass: HomeAssistant, mock_config_entry, mock_owm_client):
    """Test sensor has correct attributes."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        sensor = hass.states.get(
            f"sensor.{ENTITY_PREFIX}_test_location_rain_hourly"
        )
        assert sensor is not None
        assert "forecast_data" in sensor.attributes
        assert "location" in sensor.attributes
        assert sensor.attributes["location"]["name"] == "test_location"


@pytest.mark.asyncio
async def test_sensor_disabled_rain(hass: HomeAssistant, mock_owm_client):
    """Test rain sensors not created when disabled."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "location_name": "Test",
            "latitude": 44.9778,
            "longitude": -93.2650,
            "api_key": "test_key",
            "enable_rain": False,
            "enable_snow": True,
            "update_interval": "60",
        },
    )

    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        # Rain sensor should not exist
        rain_sensor = hass.states.get(
            f"sensor.{ENTITY_PREFIX}_test_rain_next24h"
        )
        assert rain_sensor is None

        # Snow sensor should exist
        snow_sensor = hass.states.get(
            f"sensor.{ENTITY_PREFIX}_test_snow_next24h"
        )
        assert snow_sensor is not None
'''

# tests/test_calculator.py
TEST_CALCULATOR_PY = '''"""Tests for calculator.py."""
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
    assert calc.mm_to_inches(0) == 0.0


def test_inches_to_cm():
    """Test inches to cm conversion."""
    calc = PrecipitationCalculator()
    assert calc.inches_to_cm(1.0) == 2.54
    assert calc.inches_to_cm(10.0) == 25.4
    assert calc.inches_to_cm(0) == 0.0


def test_get_snow_ratio_below_15():
    """Test snow ratio for very cold temps."""
    calc = PrecipitationCalculator()
    assert calc.get_snow_ratio(10.0) == 20.0
    assert calc.get_snow_ratio(-5.0) == 20.0


def test_get_snow_ratio_15_to_20():
    """Test snow ratio for 15-20°F."""
    calc = PrecipitationCalculator()
    assert calc.get_snow_ratio(15.0) == 18.0
    assert calc.get_snow_ratio(19.5) == 18.0


def test_get_snow_ratio_20_to_25():
    """Test snow ratio for 20-25°F."""
    calc = PrecipitationCalculator()
    assert calc.get_snow_ratio(22.0) == 15.0


def test_get_snow_ratio_25_to_30():
    """Test snow ratio for 25-30°F."""
    calc = PrecipitationCalculator()
    assert calc.get_snow_ratio(28.0) == 12.0


def test_get_snow_ratio_30_to_32():
    """Test snow ratio for 30-32°F."""
    calc = PrecipitationCalculator()
    assert calc.get_snow_ratio(31.0) == 10.0


def test_get_snow_ratio_above_32():
    """Test snow ratio above freezing."""
    calc = PrecipitationCalculator()
    assert calc.get_snow_ratio(33.0) == 0.0
    assert calc.get_snow_ratio(50.0) == 0.0


def test_mm_to_snow_inches():
    """Test complete snow calculation."""
    calc = PrecipitationCalculator()

    # 10mm liquid at 20°F (15:1 ratio)
    # 10mm = ~0.394 inches liquid
    # 0.394 * 15 = ~5.91 inches snow
    result = calc.mm_to_snow_inches(10.0, 20.0)
    assert 5.8 < result < 6.0

    # Above freezing should give 0
    assert calc.mm_to_snow_inches(10.0, 35.0) == 0.0

    # Zero precip should give 0
    assert calc.mm_to_snow_inches(0.0, 20.0) == 0.0


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
