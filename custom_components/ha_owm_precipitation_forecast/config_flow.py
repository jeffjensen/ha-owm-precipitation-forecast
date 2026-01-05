"""Config flow for OpenWeatherMap Precipitation Forecast."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import (
    CONF_API_KEY,
    CONF_LOCATION_NAME,
    CONF_SCAN_INTERVAL,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_SNOW_RATIO,
    CONF_TEMPERATURE_ADJUSTED_RATIO,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SNOW_RATIO,
    DOMAIN,
    SCAN_INTERVALS,
    LOGGER,
)
from .weather_service import OWMWeatherService

_LOGGER: logging.Logger = LOGGER


class OWMPrecipitationFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OWM Precipitation Forecast."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate API key
                session = async_get_clientsession(self.hass)
                service = OWMWeatherService(
                    api_key=user_input[CONF_API_KEY],
                    session=session,
                )
                
                await service.async_get_forecast(
                    lat=user_input[CONF_LATITUDE],
                    lon=user_input[CONF_LONGITUDE],
                )
                
                unique_id = f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_mismatch()
                
                return self.async_create_entry(
                    title=user_input.get(
                        CONF_LOCATION_NAME,
                        f"{user_input[CONF_LATITUDE]}, {user_input[CONF_LONGITUDE]}",
                    ),
                    data=user_input,
                )
            except Exception as ex:
                _LOGGER.error("Config validation failed: %s", ex)
                errors["base"] = "invalid_auth"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(
                CONF_LATITUDE,
                default=self.hass.config.latitude,
            ): vol.Range(min=-90, max=90),
            vol.Required(
                CONF_LONGITUDE,
                default=self.hass.config.longitude,
            ): vol.Range(min=-180, max=180),
            vol.Required(CONF_LOCATION_NAME, default="Home"): str,
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.In(
                SCAN_INTERVALS
            ),
            vol.Required(CONF_ENABLE_RAIN, default=True): bool,
            vol.Required(CONF_ENABLE_SNOW, default=True): bool,
            vol.Required(CONF_SNOW_RATIO, default=DEFAULT_SNOW_RATIO): vol.Range(
                min=1.0, max=50.0
            ),
            vol.Required(CONF_TEMPERATURE_ADJUSTED_RATIO, default=True): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"error": ""},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this integration."""
        return OWMPrecipitationOptionsFlow(config_entry)


class OWMPrecipitationOptionsFlow(config_entries.OptionsFlow):
    """Handle options for OWM Precipitation Forecast."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_data = self.config_entry.data
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_data.get(
                        CONF_SCAN_INTERVAL,
                        DEFAULT_SCAN_INTERVAL,
                    ),
                ): vol.In(SCAN_INTERVALS),
                vol.Required(
                    CONF_ENABLE_RAIN,
                    default=current_data.get(CONF_ENABLE_RAIN, True),
                ): bool,
                vol.Required(
                    CONF_ENABLE_SNOW,
                    default=current_data.get(CONF_ENABLE_SNOW, True),
                ): bool,
                vol.Required(
                    CONF_SNOW_RATIO,
                    default=current_data.get(CONF_SNOW_RATIO, DEFAULT_SNOW_RATIO),
                ): vol.Range(min=1.0, max=50.0),
                vol.Required(
                    CONF_TEMPERATURE_ADJUSTED_RATIO,
                    default=current_data.get(CONF_TEMPERATURE_ADJUSTED_RATIO, True),
                ): bool,
            }),
        )
