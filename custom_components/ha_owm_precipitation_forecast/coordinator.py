# Coordinates data fetching and manages updates for all sensors.
# Central data management for the integration
# Coordinates updates from the API
# Manages update intervals
# Tracks integration health
# Provides data to all sensors

"""Data coordinator for OpenWeatherMap Precipitation Forecast."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_POLL_INTERVAL,
    CONF_TEMP_RANGES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_TEMP_RANGES,
    DOMAIN,
    HEALTH_ERROR,
    HEALTH_OK,
    HEALTH_WARNING,
    LOG_UPDATE_FAILED,
    LOG_UPDATE_SUCCESS,
)
from .owm_client import OWMClient, OWMClientError
from .precipitation_calculator import PrecipitationCalculator

_LOGGER = logging.getLogger(__name__)


class OWMPrecipitationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage OpenWeatherMap data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            entry: Config entry with user configuration
        """
        self._entry = entry
        self._api_key = entry.data[CONF_API_KEY]
        self._latitude = entry.data[CONF_LATITUDE]
        self._longitude = entry.data[CONF_LONGITUDE]

        # Get poll interval from options or use default
        poll_interval_minutes = entry.options.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )
        update_interval = timedelta(minutes=poll_interval_minutes)

        # Initialize OWM client with shared session
        session = async_get_clientsession(hass)
        self._client = OWMClient(
            api_key=self._api_key,
            latitude=self._latitude,
            longitude=self._longitude,
            session=session,
        )

        # Initialize precipitation calculator with custom temp ranges if provided
        temp_ranges = entry.options.get(CONF_TEMP_RANGES, DEFAULT_TEMP_RANGES)
        self._calculator = PrecipitationCalculator(temp_ranges)

        # Health tracking
        self._health_status = HEALTH_OK
        self._health_message = "Operating normally"
        self._consecutive_errors = 0
        self._max_consecutive_errors = 3

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

        _LOGGER.info(
            "Initialized coordinator for location (%.4f, %.4f) with %d minute interval",
            self._latitude,
            self._longitude,
            poll_interval_minutes,
        )

    @property
    def health_status(self) -> str:
        """Get current health status.

        Returns:
            Health status: ok, warning, or error
        """
        return self._health_status

    @property
    def health_message(self) -> str:
        """Get current health message.

        Returns:
            Human-readable health status message
        """
        return self._health_message

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from OpenWeatherMap.

        Returns:
            Processed precipitation data

        Raises:
            UpdateFailed: If data cannot be fetched or processed
        """
        try:
            # Get raw forecast data from API
            _LOGGER.debug("Fetching forecast data from OpenWeatherMap")
            raw_data = await self._client.async_get_forecast()

            # Process and calculate precipitation
            _LOGGER.debug("Processing precipitation data")
            processed_data = self._calculator.process_forecast_data(raw_data)

            # Reset error counter on success
            self._consecutive_errors = 0
            self._health_status = HEALTH_OK
            self._health_message = "Operating normally"

            _LOGGER.debug(LOG_UPDATE_SUCCESS)
            return processed_data

        except OWMClientError as err:
            self._consecutive_errors += 1

            # Determine health status based on error count
            if self._consecutive_errors >= self._max_consecutive_errors:
                self._health_status = HEALTH_ERROR
                self._health_message = f"Multiple failures ({self._consecutive_errors}): {err}"
                _LOGGER.error(
                    "Critical: %d consecutive errors. Last error: %s",
                    self._consecutive_errors,
                    err,
                )
            else:
                self._health_status = HEALTH_WARNING
                self._health_message = f"Temporary error (attempt {self._consecutive_errors}): {err}"
                _LOGGER.warning(
                    "Warning: Error %d of %d: %s",
                    self._consecutive_errors,
                    self._max_consecutive_errors,
                    err,
                )

            _LOGGER.error(LOG_UPDATE_FAILED, err)
            raise UpdateFailed(f"Error communicating with OpenWeatherMap: {err}") from err

        except Exception as err:
            self._consecutive_errors += 1
            self._health_status = HEALTH_ERROR
            self._health_message = f"Unexpected error: {err}"

            _LOGGER.exception("Unexpected error updating data")
            raise UpdateFailed(f"Unexpected error: {err}") from err

    def update_poll_interval(self, minutes: int) -> None:
        """Update the polling interval.

        Args:
            minutes: New polling interval in minutes
        """
        self.update_interval = timedelta(minutes=minutes)
        _LOGGER.info("Updated poll interval to %d minutes", minutes)

    def update_temperature_ranges(
        self, temp_ranges: dict[str, dict[str, float]]
    ) -> None:
        """Update temperature ranges for snow calculations.

        Args:
            temp_ranges: New temperature range configuration
        """
        self._calculator = PrecipitationCalculator(temp_ranges)
        _LOGGER.info("Updated temperature ranges for snow calculations")
