"""Config flow for OWM Precipitation Forecast integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol
from aiohttp import ClientResponseError
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.util import slugify

from .client import OWMClient, OWMCoordinates
from .const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LOCATION_SLUG,
    CONF_LONGITUDE,
    CONF_POLLING_INTERVAL,
    CONF_SNOW_RATIO_MODE,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_SNOW_RATIO_MODE,
    DOMAIN,
    POLLING_INTERVAL_OPTIONS,
)
from .coordinator import OWMPrecipitationCoordinator
from .exceptions import OWMPrecipitationAPIError, OWMPrecipitationConfigError

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA_STEP_USER = vol.Schema(
    {
        vol.Required(CONF_API_KEY): selector.TextSelector(),
        vol.Required(CONF_LOCATION_NAME): selector.TextSelector(),
        vol.Required(CONF_LATITUDE): selector.TextSelector(
            text_filter={"mode": "float"},
        ),
        vol.Required(CONF_LONGITUDE): selector.TextSelector(
            text_filter={"mode": "float"},
        ),
    }
)

POLLING_INTERVAL_SELECTOR = selector.SelectSelector(
    options=list(POLLING_INTERVAL_OPTIONS.keys()),
    mode="dropdown",
)

SNOW_RATIO_MODE_SELECTOR = selector.SelectSelector(
    options=["preset", "custom"],
    mode="dropdown",
)


class OWMPrecipitationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for OWM Precipitation Forecast."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize config flow."""
        self._config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate API key and coordinates by making test call
                await self._test_owm_connection(
                    user_input[CONF_API_KEY],
                    float(user_input[CONF_LATITUDE]),
                    float(user_input[CONF_LONGITUDE]),
                )
            except OWMPrecipitationAPIError as err:
                _LOGGER.error("OWM API validation failed: %s", err)
                errors[CONF_API_KEY] = "invalid_api_key"
            except ValueError as err:
                errors["base"] = "invalid_coordinates"
            else:
                # Generate slug from location name
                location_slug = self._generate_slug(user_input[CONF_LOCATION_NAME])

                # Check for existing entry
                if self._entry_exists(location_slug):
                    return self.async_abort(reason="already_configured")

                self._config.update(user_input)
                self._config[CONF_LOCATION_SLUG] = location_slug

                return await self.async_step_confirm()

            # Update errors for re-render
            errors = {**errors, **user_input}

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA_STEP_USER,
            errors=errors,
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm location and generate config."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._config[CONF_LOCATION_NAME],
                data=self._config,
                options={
                    CONF_POLLING_INTERVAL: DEFAULT_POLLING_INTERVAL,
                    CONF_SNOW_RATIO_MODE: DEFAULT_SNOW_RATIO_MODE,
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "location": self._config[CONF_LOCATION_NAME],
                "lat": self._config[CONF_LATITUDE],
                "lon": self._config[CONF_LONGITUDE],
            },
        )

    @staticmethod
    def _generate_slug(location_name: str) -> str:
        """Generate a slug from location name."""
        slug = slugify(location_name)
        # Ensure minimum length and valid characters
        slug = re.sub(r"[^a-z0-9_-]", "_", slug.lower())
        slug = re.sub(r"_+", "_", slug)
        return slug[:32] or "location"

    def _entry_exists(self, location_slug: str) -> bool:
        """Return true if entry with location slug exists."""
        return any(
            entry.data.get(CONF_LOCATION_SLUG) == location_slug
            for entry in self._async_current_entries()
        )

    async def _test_owm_connection(
        self, api_key: str, latitude: float, longitude: float
    ) -> None:
        """Test OWM connection with provided credentials."""
        hass = self.hass
        coords = OWMCoordinates(latitude=latitude, longitude=longitude)
        client = OWMClient(hass, api_key, coords)

        # Just fetch data, don't process it
        await client.async_get_forecast()


class OWMPrecipitationOptionsFlow(config_entries.OptionsFlow):
    """Options flow for OWM Precipitation Forecast."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=self._schema_from_options(current_options),
        )

    def _schema_from_options(self, options: dict[str, Any]) -> vol.Schema:
        """Generate schema from current options."""
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLLING_INTERVAL,
                    default=options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
                ): POLLING_INTERVAL_SELECTOR,
                vol.Optional(
                    CONF_SNOW_RATIO_MODE,
                    default=options.get(CONF_SNOW_RATIO_MODE, DEFAULT_SNOW_RATIO_MODE),
                ): SNOW_RATIO_MODE_SELECTOR,
            }
        )

        # Add snow ratio preset selector if preset mode
        if options.get(CONF_SNOW_RATIO_MODE) == "preset":
            schema = schema.extend(
                {
                    vol.Optional(
                        "snow_ratio_preset",
                        default=options.get("snow_ratio_preset", "default"),
                    ): selector.SelectSelector(
                        options=["default", "dry", "wet"],
                        mode="dropdown",
                    ),
                }
            )

        return schema
