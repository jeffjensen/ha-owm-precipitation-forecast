"""Config flow for OWM Precipitation Forecast integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_POLLING_INTERVAL,
    CONF_SNOW_RATIOS,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_SNOW_RATIOS,
    DOMAIN,
    ERROR_API_CONNECTION,
    ERROR_API_KEY_INVALID,
    ERROR_LOCATION_INVALID,
    ERROR_UNKNOWN,
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
    POLLING_INTERVAL_OPTIONS,
    POLLING_INTERVALS,
)

_LOGGER = logging.getLogger(__name__)


def _validate_location(latitude: float, longitude: float) -> bool:
    """Validate location coordinates."""
    return (
        MIN_LATITUDE <= latitude <= MAX_LATITUDE
        and MIN_LONGITUDE <= longitude <= MAX_LONGITUDE
    )


async def _validate_api_key(hass: HomeAssistant, api_key: str) -> dict[str, Any]:
    """Validate the API key by making a test call."""
    from .api_client import OWMApiClient

    client = OWMApiClient(api_key, hass)

    try:
        # Test with a known good location (San Francisco)
        await client.get_forecast(37.7749, -122.4194)
        return {"title": "API Key Valid"}
    except Exception as err:
        _LOGGER.error("API key validation failed: %s", err)
        raise


class OWMPrecipitationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OWM Precipitation Forecast."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate API key
            try:
                await _validate_api_key(self.hass, user_input[CONF_API_KEY])
            except Exception:
                errors["base"] = ERROR_API_KEY_INVALID

            # Validate location
            if not _validate_location(
                user_input[CONF_LATITUDE], user_input[CONF_LONGITUDE]
            ):
                errors["base"] = ERROR_LOCATION_INVALID

            if not errors:
                # Check if location already configured
                await self.async_set_unique_id(
                    f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}"
                )
                self._abort_if_unique_id_configured()

                # Create entry
                return self.async_create_entry(
                    title=user_input[CONF_LOCATION_NAME],
                    data={
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_LOCATION_NAME: user_input[CONF_LOCATION_NAME],
                        CONF_LATITUDE: user_input[CONF_LATITUDE],
                        CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                    },
                    options={
                        CONF_ENABLE_RAIN: user_input.get(
                            CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN
                        ),
                        CONF_ENABLE_SNOW: user_input.get(
                            CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW
                        ),
                        CONF_POLLING_INTERVAL: POLLING_INTERVALS[
                            user_input.get("polling_interval_option", "1_hour")
                        ],
                        CONF_SNOW_RATIOS: DEFAULT_SNOW_RATIOS,
                    },
                )

        # Get default location from Home Assistant
        default_latitude = self.hass.config.latitude
        default_longitude = self.hass.config.longitude

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(
                    CONF_LOCATION_NAME, default="Home"
                ): cv.string,
                vol.Required(
                    CONF_LATITUDE, default=default_latitude
                ): cv.latitude,
                vol.Required(
                    CONF_LONGITUDE, default=default_longitude
                ): cv.longitude,
                vol.Required(
                    CONF_ENABLE_RAIN, default=DEFAULT_ENABLE_RAIN
                ): cv.boolean,
                vol.Required(
                    CONF_ENABLE_SNOW, default=DEFAULT_ENABLE_SNOW
                ): cv.boolean,
                vol.Required(
                    "polling_interval_option", default="1_hour"
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=POLLING_INTERVAL_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="polling_interval",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OWMPrecipitationOptionsFlow(config_entry)


class OWMPrecipitationOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for OWM Precipitation Forecast."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Convert polling interval option to seconds
            polling_interval = POLLING_INTERVALS.get(
                user_input.get("polling_interval_option", "1_hour"),
                DEFAULT_POLLING_INTERVAL,
            )

            return self.async_create_entry(
                title="",
                data={
                    CONF_ENABLE_RAIN: user_input[CONF_ENABLE_RAIN],
                    CONF_ENABLE_SNOW: user_input[CONF_ENABLE_SNOW],
                    CONF_POLLING_INTERVAL: polling_interval,
                    CONF_SNOW_RATIOS: self.config_entry.options.get(
                        CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS
                    ),
                },
            )

        # Get current polling interval option
        current_polling_interval = self.config_entry.options.get(
            CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
        )
        current_polling_option = "1_hour"
        for option, seconds in POLLING_INTERVALS.items():
            if seconds == current_polling_interval:
                current_polling_option = option
                break

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENABLE_RAIN,
                    default=self.config_entry.options.get(
                        CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN
                    ),
                ): cv.boolean,
                vol.Required(
                    CONF_ENABLE_SNOW,
                    default=self.config_entry.options.get(
                        CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW
                    ),
                ): cv.boolean,
                vol.Required(
                    "polling_interval_option",
                    default=current_polling_option,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=POLLING_INTERVAL_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key="polling_interval",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )

    async def async_step_snow_ratios(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure temperature-adjusted snow ratios."""
        if user_input is not None:
            # Update snow ratios
            return self.async_create_entry(
                title="",
                data={
                    **self.config_entry.options,
                    CONF_SNOW_RATIOS: user_input,
                },
            )

        current_ratios = self.config_entry.options.get(
            CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    "ratio_32",
                    default=current_ratios.get("32", 10.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_28",
                    default=current_ratios.get("28", 12.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_24",
                    default=current_ratios.get("24", 15.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_20",
                    default=current_ratios.get("20", 20.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_15",
                    default=current_ratios.get("15", 25.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_10",
                    default=current_ratios.get("10", 30.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_0",
                    default=current_ratios.get("0", 40.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
                vol.Required(
                    "ratio_minus_10",
                    default=current_ratios.get("-10", 50.0),
                ): vol.All(vol.Coerce(float), vol.Range(min=5.0, max=100.0)),
            }
        )

        return self.async_show_form(
            step_id="snow_ratios",
            data_schema=data_schema,
        )
