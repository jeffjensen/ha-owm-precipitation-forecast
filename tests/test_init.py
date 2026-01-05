"""Tests for __init__.py."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState

from custom_components.ha_owm_precipitation_forecast.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_config_entry, mock_owm_client):
    """Test setup entry."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state == ConfigEntryState.LOADED
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_config_entry, mock_owm_client):
    """Test unloading entry."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
        assert mock_config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_coordinator_update_success(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test coordinator successfully updates data."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
        await coordinator.async_refresh()

        assert coordinator.data is not None
        assert coordinator.last_update_success
        assert coordinator.error_count == 0


@pytest.mark.asyncio
async def test_coordinator_update_failure(
    hass: HomeAssistant, mock_config_entry, mock_owm_client
):
    """Test coordinator handles update failure."""
    mock_owm_client.get_forecast_data.side_effect = Exception("API Error")

    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)

        # Setup should succeed even if first update fails
        with pytest.raises(Exception):
            assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
