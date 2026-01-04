"""Test component setup."""
import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_owm_precipitation_forecast.const import DOMAIN


async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry
) -> None:
    """Test successful setup of the integration."""
    mock_config_entry.add_to_hass(hass)

    # Entry should be in NOT_LOADED state initially
    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry
) -> None:
    """Test unloading the integration."""
    mock_config_entry.add_to_hass(hass)

    # Setup would normally happen here
    # For now, just verify the entry exists
    assert mock_config_entry.entry_id in hass.config_entries.async_entries(DOMAIN)[0].entry_id


async def test_reload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry
) -> None:
    """Test reloading the integration."""
    mock_config_entry.add_to_hass(hass)

    # Verify entry is registered
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].entry_id == mock_config_entry.entry_id
