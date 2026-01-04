# UI configuration flow for setting up and configuring the integration.
# UI-based configuration
# Initial setup flow
# Options/configuration flow
# API validation

"""Config flow for OpenWeatherMap Precipitation Forecast."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_POLL_INTERVAL,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_LOCATION_NAME,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    POLL_INTERVALS,
)
from .owm_client import OWMClient, OWMClientError

_LOGGER = logging.getLogger(__name__)


class OWMPrecipitationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenWeatherMap Precipitation Forecast."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step.

        Args:
            user_input: User-provided configuration data

        Returns:
            FlowResult for next step or entry creation
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate the API key and connection
                await self._validate_input(self.hass, user_input)

            except OWMClientError as err:
                # Map OWM errors to UI error messages
                if err.error_code == "invalid_api_key":
                    errors["base"] = "invalid_auth"
                    _LOGGER.warning("Invalid API key provided")
                elif err.error_code == "rate_limited":
                    errors["base"] = "rate_limited"
                    _LOGGER.warning("API rate limit exceeded during setup")
                else:
                    errors["base"] = "cannot_connect"
                    _LOGGER.error("Cannot connect to OpenWeatherMap: %s", err)

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during setup")
                errors["base"] = "unknown"

            else:
                # Create unique ID from coordinates
                await self.async_set_unique_id(
                    f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}"
                )
                self._abort_if_unique_id_configured()

                # Create the config entry
                return self.async_create_entry(
                    title=user_input.get(CONF_LOCATION_NAME, DEFAULT_LOCATION_NAME),
                    data=user_input,
                )

        # Show the configuration form
        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(
                CONF_LATITUDE,
                default=self.hass.config.latitude
            ): cv.latitude,
            vol.Required(
                CONF_LONGITUDE,
                default=self.hass.config.longitude
            ): cv.longitude,
            vol.Optional(
                CONF_LOCATION_NAME,
                default=DEFAULT_LOCATION_NAME
            ): str,
            vol.Optional(
                CONF_ENABLE_RAIN,
                default=DEFAULT_ENABLE_RAIN
            ): bool,
            vol.Optional(
                CONF_ENABLE_SNOW,
                default=DEFAULT_ENABLE_SNOW
            ): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_url": "https://openweathermap.org/api",
            }
        )

    async def _validate_input(
        self, hass: HomeAssistant, data: dict[str, Any]
    ) -> None:
        """Validate the user input allows us to connect.

        Args:
            hass: Home Assistant instance
            data: User-provided configuration

        Raises:
            OWMClientError: If validation fails
        """
        # Create a temporary client to test the connection
        client = OWMClient(
            api_key=data[CONF_API_KEY],
            latitude=data[CONF_LATITUDE],
            longitude=data[CONF_LONGITUDE],
        )

        try:
            # Attempt to fetch forecast to validate API key and connection
            await client.async_get_forecast()
            _LOGGER.info("Successfully validated API connection")
        finally:
            # Always close the client session
            await client.async_close()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OWMPrecipitationOptionsFlow:
        """Get the options flow for this handler.

        Args:
            config_entry: The config entry to get options for

        Returns:
            Options flow handler
        """
        return OWMPrecipitationOptionsFlow(config_entry)


class OWMPrecipitationOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for OpenWeatherMap Precipitation Forecast."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: The config entry being configured
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options.

        Args:
            user_input: User-provided option values

        Returns:
            FlowResult for completion or form display
        """
        if user_input is not None:
            # Update options and reload the integration
            return self.async_create_entry(title="", data=user_input)

        # Show the options form with current values
        data_schema = vol.Schema({
            vol.Optional(
                CONF_ENABLE_RAIN,
                default=self.config_entry.options.get(
                    CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN
                ),
            ): bool,
            vol.Optional(
                CONF_ENABLE_SNOW,
                default=self.config_entry.options.get(
                    CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW
                ),
            ): bool,
            vol.Optional(
                CONF_POLL_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                ),
            ): vol.In(POLL_INTERVALS),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={
                "location": self.config_entry.data.get(
                    CONF_LOCATION_NAME, DEFAULT_LOCATION_NAME
                ),
            }
        )
