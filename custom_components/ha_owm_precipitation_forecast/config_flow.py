"""Config flow for OpenWeatherMap Precipitation Forecast integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_SNOW_RATIOS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_LOCATION_NAME,
    DEFAULT_SNOW_RATIOS,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER_NAME,
    UPDATE_INTERVALS,
)
from .owm_client import OpenWeatherMapClient, OpenWeatherMapError

_LOGGER = logging.getLogger(LOGGER_NAME)


async def validate_api_credentials(
    hass: HomeAssistant, api_key: str, latitude: float, longitude: float
) -> dict[str, Any]:
    """Validate API credentials."""
    client = OpenWeatherMapClient(api_key, latitude, longitude)
    try:
        await client.validate_credentials()
        return {"title": f"Location ({latitude}, {longitude})"}
    except OpenWeatherMapError as err:
        _LOGGER.error("Validation failed: %s", err)
        raise


class OWMPrecipitationForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate coordinates
                lat = user_input[CONF_LATITUDE]
                lon = user_input[CONF_LONGITUDE]
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    errors["base"] = "invalid_coordinates"
                else:
                    # Validate API key
                    info = await validate_api_credentials(
                        self.hass,
                        user_input[CONF_API_KEY],
                        lat,
                        lon,
                    )
                    
                    # Check if already configured
                    await self.async_set_unique_id(
                        f"{lat}_{lon}_{user_input.get(CONF_LOCATION_NAME, DEFAULT_LOCATION_NAME)}"
                    )
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(title=info["title"], data=user_input)
                    
            except OpenWeatherMapError:
                errors["base"] = "invalid_api_key"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Build schema
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOCATION_NAME, default=DEFAULT_LOCATION_NAME
                ): selector.TextSelector(),
                vol.Required(CONF_LATITUDE): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=-90, max=90, step=0.0001, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Required(CONF_LONGITUDE): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=-180, max=180, step=0.0001, mode=selector.NumberSelectorMode.BOX
                    )
                ),
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required(
                    CONF_ENABLE_RAIN, default=DEFAULT_ENABLE_RAIN
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_ENABLE_SNOW, default=DEFAULT_ENABLE_SNOW
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_UPDATE_INTERVAL, default=str(DEFAULT_UPDATE_INTERVAL)
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=str(v), label=k)
                            for k, v in UPDATE_INTERVALS.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OWMPrecipitationForecastOptionsFlow:
        """Get the options flow."""
        return OWMPrecipitationForecastOptionsFlow(config_entry)


class OWMPrecipitationForecastOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values
        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            self.config_entry.data.get(CONF_UPDATE_INTERVAL, str(DEFAULT_UPDATE_INTERVAL)),
        )
        current_rain = self.config_entry.options.get(
            CONF_ENABLE_RAIN,
            self.config_entry.data.get(CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN),
        )
        current_snow = self.config_entry.options.get(
            CONF_ENABLE_SNOW,
            self.config_entry.data.get(CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW),
        )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ENABLE_RAIN, default=current_rain): selector.BooleanSelector(),
                vol.Required(CONF_ENABLE_SNOW, default=current_snow): selector.BooleanSelector(),
                vol.Required(
                    CONF_UPDATE_INTERVAL, default=str(current_interval)
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=str(v), label=k)
                            for k, v in UPDATE_INTERVALS.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
