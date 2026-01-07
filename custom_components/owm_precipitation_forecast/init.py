"""OpenWeatherMap Precipitation Forecast integration for Home Assistant.

This integration provides precipitation forecasts (rain and snow) from
OpenWeatherMap with configurable polling intervals and temperature-adjusted
snow ratio calculations.
"""

from __future__ import annotations

import logging
from typing import Final

from const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER: Final = logging.getLogger(__name__)

PLATFORMS: Final = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenWeatherMap Precipitation Forecast from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry from user setup

    Returns:
        True if setup successful, False otherwise
    """
    _LOGGER.debug("Setting up %s", DOMAIN)

    hass.data.setdefault(DOMAIN, {})

    # Store the entry
    hass.data[DOMAIN][entry.entry_id] = {
        "entry": entry,
    }

    # Set up platforms will be done in Phase 3
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenWeatherMap Precipitation Forecast config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry to unload

    Returns:
        True if unload successful, False otherwise
    """
    _LOGGER.debug("Unloading %s", DOMAIN)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload OpenWeatherMap Precipitation Forecast config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry to reload
    """
    _LOGGER.debug("Reloading %s", DOMAIN)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
