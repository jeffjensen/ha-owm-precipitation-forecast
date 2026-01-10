"""Test OWM Precipitation Forecast init."""
import pytest
from homeassistant.core import HomeAssistant

from custom_components.owm_precipitation_forecast import (DOMAIN,
                                                          async_setup_entry,
                                                          async_unload_entry)


async def test_async_setup_entry(hass: HomeAssistant, mock_config_entry):
    """Test async setup entry."""
    assert await async_setup_entry(hass, mock_config_entry)

async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry):
    """Test async unload entry."""
    mock_config_entry.added_config.setups = {"sensor": True}
    assert await async_unload_entry(hass, mock_config_entry)
    mock_config_entry.added_config.setups = {"sensor": True}
    assert await async_unload_entry(hass, mock_config_entry)
