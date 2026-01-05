"""Tests for binary_sensor.py."""
import pytest
from unittest.mock import patch

from homeassistant.core import HomeAssistant

from custom_components.ha_owm_precipitation_forecast.const import (
    DOMAIN,
    ENTITY_PREFIX,
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
)


@pytest.mark.asyncio
async def test_health_sensor_setup(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor setup."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )
        assert health_sensor is not None
        assert health_sensor.state in ["on", "off"]


@pytest.mark.asyncio
async def test_health_sensor_ok_status(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor shows OK when no errors."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )

        assert health_sensor.state == "off"
        assert health_sensor.attributes["api_status"] == STATUS_OK
        assert health_sensor.attributes["error_count"] == 0


@pytest.mark.asyncio
async def test_health_sensor_warning_status(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor shows warning with few errors."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
        coordinator.error_count = 2
        coordinator.last_error = "Minor API error"

        await coordinator.async_refresh()
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )

        assert health_sensor.state == "off"
        assert health_sensor.attributes["api_status"] == STATUS_WARNING
        assert health_sensor.attributes["error_count"] == 2


@pytest.mark.asyncio
async def test_health_sensor_error_status(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor shows error with many errors."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
        coordinator.error_count = 5
        coordinator.last_error = "Critical API error"

        await coordinator.async_refresh()
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )

        assert health_sensor.state == "on"
        assert health_sensor.attributes["api_status"] == STATUS_ERROR
        assert health_sensor.attributes["error_count"] == 5
        assert health_sensor.attributes["last_error"] == "Critical API error"


@pytest.mark.asyncio
async def test_health_sensor_attributes(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor has correct attributes."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )

        assert "last_update" in health_sensor.attributes
        assert "api_status" in health_sensor.attributes
        assert "error_count" in health_sensor.attributes
        assert "last_error" in health_sensor.attributes

        assert health_sensor.attributes["api_status"] == STATUS_OK
        assert health_sensor.attributes["error_count"] == 0
        assert health_sensor.attributes["last_error"] is None


@pytest.mark.asyncio
async def test_health_sensor_device_class(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor has correct device class."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )

        assert health_sensor.attributes.get("device_class") == "problem"


@pytest.mark.asyncio
async def test_health_sensor_updates_with_coordinator(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test health sensor updates when coordinator updates."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )
        initial_update = health_sensor.attributes.get("last_update")

        await coordinator.async_refresh()
        await hass.async_block_till_done()

        health_sensor = hass.states.get(
            f"binary_sensor.{ENTITY_PREFIX}_test_location_health"
        )
        new_update = health_sensor.attributes.get("last_update")

        assert new_update is not None
