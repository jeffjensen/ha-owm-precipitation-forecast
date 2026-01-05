"""OpenWeatherMap Precipitation Forecast Integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER_NAME,
)
from .owm_client import OpenWeatherMapClient, OpenWeatherMapError

_LOGGER = logging.getLogger(LOGGER_NAME)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenWeatherMap Precipitation Forecast from a config entry."""
    _LOGGER.info(
        "Setting up %s integration for location: %s",
        DOMAIN,
        entry.data.get("location_name"),
    )

    coordinator = PrecipitationForecastCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info(
        "Unloading %s integration for location: %s",
        DOMAIN,
        entry.data.get("location_name"),
    )

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    _LOGGER.debug("Options updated for %s", entry.data.get("location_name"))
    await hass.config_entries.async_reload(entry.entry_id)


class PrecipitationForecastCoordinator(DataUpdateCoordinator):
    """Class to manage fetching precipitation forecast data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.client = OpenWeatherMapClient(
            api_key=entry.data["api_key"],
            latitude=entry.data["latitude"],
            longitude=entry.data["longitude"],
        )

        update_interval = entry.options.get(
            CONF_UPDATE_INTERVAL, entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        # Convert string to int if needed
        if isinstance(update_interval, str):
            update_interval = int(update_interval)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data.get('location_name', 'unknown')}",
            update_interval=timedelta(minutes=update_interval),
        )

        self.last_error: str | None = None
        self.error_count: int = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            _LOGGER.debug("Fetching precipitation forecast data")
            data = await self.client.get_forecast_data()
            self.last_error = None
            _LOGGER.info("Successfully fetched precipitation forecast data")
            return data
        except OpenWeatherMapError as err:
            self.error_count += 1
            self.last_error = str(err)
            _LOGGER.error(
                "Error fetching data: %s (error count: %d)", err, self.error_count
            )
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            self.error_count += 1
            self.last_error = str(err)
            _LOGGER.exception("Unexpected error fetching data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
