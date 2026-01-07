from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
)

class OWMPrecipitationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="OWM Precipitation Forecast", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_LATITUDE): float,
            vol.Required(CONF_LONGITUDE): float,
            vol.Optional(CONF_ENABLE_RAIN, default=DEFAULT_ENABLE_RAIN): bool,
            vol.Optional(CONF_ENABLE_SNOW, default=DEFAULT_ENABLE_SNOW): bool,
        })
        return self.async_show_form(step_id="user", data_schema=schema)
