"""OWM Precipitation Forecast integration for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
import voluptuous as vol
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OWMPrecipitationTransformer
from .client import OWMClient, OWMCoordinates
from .const import (
    CONF_API_KEY,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_LOCATION_SLUG,
    CONF_POLLING_INTERVAL,
    CONF_SNOW_RATIO_CONFIG,
    CONF_SNOW_RATIO_MODE,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_SNOW_RATIO_MODE,
    DOMAIN,
    POLLING_INTERVAL_OPTIONS,
)
from .coordinator import OWMPrecipitationCoordinator
from .exceptions import OWMPrecipitationError
from .snow_ratio import SnowRatioCalculator, SNOW_RATIO_PRESETS

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

CONFIG_SCHEMA = cv.DEP_CONFIG_DOMAIN_SCHEMA(DOMAIN, {})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OWM Precipitation Forecast from a config entry."""
    try:
        coordinator = await _async_create_coordinator(hass, entry)
        snow_ratio = _create_snow_ratio_calculator(entry)

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "coordinator": coordinator,
            "snow_ratio": snow_ratio,
        }

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        entry.async_on_unload(
            entry.add_update_listener(_async_update_entry)
        )

        _LOGGER.info(
            "OWM Precipitation Forecast setup complete for %s",
            entry.data[CONF_LOCATION_NAME]
        )
        return True

    except OWMPrecipitationError as err:
        _LOGGER.error("Failed to setup %s: %s", entry.title, err)
        return False

async def _async_create_coordinator(
    hass: HomeAssistant, entry: ConfigEntry
) -> OWMPrecipitationCoordinator:
    """Create and initialize the data coordinator."""
    api_key = entry.data[CONF_API_KEY]
    lat = entry.data[CONF_LATITUDE]
    lon = entry.data[CONF_LONGITUDE]

    coords = OWMCoordinates(latitude=lat, longitude=lon)
    client = OWMClient(hass, api_key, coords)

    # Get polling interval from options, fallback to data
    polling_minutes = entry.options.get(
        CONF_POLLING_INTERVAL, entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
    )
    polling_interval = POLLING_INTERVAL_OPTIONS.get(polling_minutes, POLLING_INTERVAL_OPTIONS[DEFAULT_POLLING_INTERVAL])

    coordinator = OWMPrecipitationCoordinator(hass, client, polling_interval)

    # Initial update
    await coordinator.async_config_entry_first_refresh()
    return coordinator

def _create_snow_ratio_calculator(entry: ConfigEntry) -> SnowRatioCalculator:
    """Create snow ratio calculator from config entry options."""
    snow_ratio_mode = entry.options.get(
        CONF_SNOW_RATIO_MODE, DEFAULT_SNOW_RATIO_MODE
    )

    if snow_ratio_mode == "preset":
        preset_name = entry.options.get("snow_ratio_preset", "default")
        config = SNOW_RATIO_PRESETS.get(preset_name, SNOW_RATIO_PRESETS["default"])
    else:
        # Custom mode uses explicit config
        config = entry.options.get(CONF_SNOW_RATIO_CONFIG, {})

    return SnowRatioCalculator(config)

async def _async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload coordinator when options change."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OWM Precipitation Forecast config entry."""
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data and not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    _LOGGER.info("Unloaded OWM Precipitation Forecast: %s", entry.title)
    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating config entry from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}

        # Add defaults for new options
        new[CONF_ENABLE_RAIN] = DEFAULT_ENABLE_RAIN
        new[CONF_ENABLE_SNOW] = DEFAULT_ENABLE_SNOW
        new[CONF_POLLING_INTERVAL] = DEFAULT_POLLING_INTERVAL

        # Generate location slug if missing
        if CONF_LOCATION_SLUG not in new:
            location_name = new[CONF_LOCATION_NAME]
            new[CONF_LOCATION_SLUG] = (
                location_name.lower()
                .replace(" ", "_")
                .replace("-", "_")
                .replace(".", "")
            )

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migrated config entry to version %s", config_entry.version)
    return True
