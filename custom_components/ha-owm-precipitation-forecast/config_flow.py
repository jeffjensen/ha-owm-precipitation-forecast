import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

from .const import DOMAIN, CONF_LOCATION_NAME, OWM_API_URL, CONF_ENABLE_RAIN, CONF_ENABLE_SNOW, CONF_POLL_INTERVAL, CONF_SNOW_RATIOS, DEFAULT_POLL_INTERVAL, DEFAULT_SNOW_RATIOS, POLL_INTERVALS
from .coordinator import OWMPrecipForecastCoordinator

_LOGGER = logging.getLogger(__name__)

class OWMPrecipForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            coordinator = OWMPrecipForecastCoordinator(self.hass, self._get_temp_entry(user_input), session)
            try:
                await coordinator.async_refresh()
                if coordinator.last_update_success:
                    return self.async_create_entry(title=user_input[CONF_LOCATION_NAME], data=user_input)
                errors["base"] = "invalid_api_key"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_LOCATION_NAME): str,
                vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): float,
                vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): float,
            }),
            errors=errors,
        )

    def _get_temp_entry(self, user_input):
        return self.hass.config_entries._async_create_mock_entry(domain=DOMAIN, data=user_input, options={})

class OWMPrecipForecastOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_ENABLE_RAIN, default=self.config_entry.options.get(CONF_ENABLE_RAIN, True)): bool,
                vol.Optional(CONF_ENABLE_SNOW, default=self.config_entry.options.get(CONF_ENABLE_SNOW, True)): bool,
                vol.Optional(CONF_POLL_INTERVAL, default=list(POLL_INTERVALS.keys())[2]): vol.In(list(POLL_INTERVALS.keys())),
                vol.Optional(CONF_SNOW_RATIOS, default=self.config_entry.options.get(CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS)): str,
            }),
        )
