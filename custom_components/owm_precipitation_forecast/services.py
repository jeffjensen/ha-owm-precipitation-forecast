"""Service handlers for OWM Precipitation Forecast."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN, SERVICE_CLEAR_ERRORS, SERVICE_UPDATE_FORECAST
from .coordinator import OWMPrecipitationCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for OWM Precipitation Forecast."""

    async def handle_update_forecast(call: ServiceCall) -> None:
        """Handle the update_forecast service call."""
        _LOGGER.info("Manual forecast update requested")

        # Get all coordinators from all config entries
        updated_count = 0
        error_count = 0

        for entry in hass.config_entries.async_entries(DOMAIN):
            try:
                coordinator: OWMPrecipitationCoordinator = entry.runtime_data
                await coordinator.async_request_refresh()
                updated_count += 1
                _LOGGER.debug(
                    "Requested refresh for %s", coordinator.location_name
                )
            except Exception as err:
                error_count += 1
                _LOGGER.error(
                    "Failed to refresh %s: %s",
                    entry.data.get("location_name", "unknown"),
                    err,
                )

        _LOGGER.info(
            "Manual forecast update completed (success: %d, errors: %d)",
            updated_count,
            error_count,
        )

    async def handle_clear_errors(call: ServiceCall) -> None:
        """Handle the clear_errors service call."""
        _LOGGER.info("Clearing errors for all locations")

        # Get all coordinators from all config entries
        cleared_count = 0

        for entry in hass.config_entries.async_entries(DOMAIN):
            try:
                coordinator: OWMPrecipitationCoordinator = entry.runtime_data
                coordinator.clear_errors()
                cleared_count += 1
                _LOGGER.debug(
                    "Cleared errors for %s", coordinator.location_name
                )
            except Exception as err:
                _LOGGER.error(
                    "Failed to clear errors for %s: %s",
                    entry.data.get("location_name", "unknown"),
                    err,
                )

        _LOGGER.info("Cleared errors for %d locations", cleared_count)

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_FORECAST,
        handle_update_forecast,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_ERRORS,
        handle_clear_errors,
    )

    _LOGGER.info("Services registered: %s, %s", SERVICE_UPDATE_FORECAST, SERVICE_CLEAR_ERRORS)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for OWM Precipitation Forecast."""
    # Only unload if no more config entries
    if not hass.config_entries.async_entries(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_FORECAST)
        hass.services.async_remove(DOMAIN, SERVICE_CLEAR_ERRORS)
        _LOGGER.info("Services unloaded")
