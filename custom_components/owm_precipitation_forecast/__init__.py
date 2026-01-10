"""The OWM Precipitation Forecast integration."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS
from .coordinator import OWMPrecipitationCoordinator
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

type OWMConfigEntry = ConfigEntry[OWMPrecipitationCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: OWMConfigEntry) -> bool:
    """Set up OWM Precipitation Forecast from a config entry."""
    _LOGGER.debug("Setting up OWM Precipitation Forecast integration for %s", entry.title)

    # Create coordinator
    coordinator = OWMPrecipitationCoordinator(hass, entry)

    # Perform initial data fetch
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to fetch initial data: %s", err)
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {err}") from err

    # Store coordinator
    entry.runtime_data = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Set up services (only once)
    if not hass.services.has_service(DOMAIN, "update_forecast"):
        await async_setup_services(hass)

    _LOGGER.info("Successfully set up OWM Precipitation Forecast for %s", entry.title)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: OWMConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading OWM Precipitation Forecast integration for %s", entry.title)

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Unload services if this is the last entry
    if unload_ok:
        await async_unload_services(hass)

    if unload_ok:
        _LOGGER.info("Successfully unloaded OWM Precipitation Forecast for %s", entry.title)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: OWMConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("Updating options for %s", entry.title)

    # Reload the config entry to apply new options
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", entry.version)

    if entry.version == 1:
        # No migration needed for version 1
        return True

    # If migration fails, return False
    _LOGGER.error("Migration from version %s failed", entry.version)
    return False
