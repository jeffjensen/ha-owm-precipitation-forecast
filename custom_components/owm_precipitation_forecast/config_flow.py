"""Config flow for OpenWeatherMap Precipitation Forecast integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from const import (
    CONF_API_KEY,
    CONF_LOCATION_NAME,
    DOMAIN,
    ERROR_ALREADY_CONFIGURED,
    # ERROR_CANNOT_CONNECT,
    ERROR_INVALID_API_KEY,
    # ERROR_INVALID_LOCATION,
)
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult


class OWMPrecipitationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenWeatherMap Precipitation Forecast."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step initiated by the user."""
        self._errors = {}

        if user_input is not None:
            # Basic validation stubs; fill in real API validation in later phase
            api_key = user_input[CONF_API_KEY]
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]
            location_name = user_input[CONF_LOCATION_NAME]

            # Ensure location not already configured
            await self.async_set_unique_id(f"{latitude},{longitude}")
            self._abort_if_unique_id_configured(reason=ERROR_ALREADY_CONFIGURED)

            if not api_key:
                self._errors["base"] = ERROR_INVALID_API_KEY
            else:
                # For Phase 1, accept values without doing real API calls
                return self.async_create_entry(
                    title=location_name,
                    data={
                        CONF_API_KEY: api_key,
                        CONF_LATITUDE: latitude,
                        CONF_LONGITUDE: longitude,
                        CONF_LOCATION_NAME: location_name,
                    },
                )

        return self._show_user_form(user_input)

    @callback
    def _show_user_form(self, user_input: dict[str, Any] | None) -> FlowResult:
        """Show the configuration form to edit or create a config entry."""
        if user_input is None:
            user_input = {}

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY, default=user_input.get(CONF_API_KEY, "")
                ): str,
                vol.Required(
                    CONF_LATITUDE, default=user_input.get(CONF_LATITUDE, 0.0)
                ): float,
                vol.Required(
                    CONF_LONGITUDE, default=user_input.get(CONF_LONGITUDE, 0.0)
                ): float,
                vol.Required(
                    CONF_LOCATION_NAME,
                    default=user_input.get(CONF_LOCATION_NAME, "Home"),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors,
        )
