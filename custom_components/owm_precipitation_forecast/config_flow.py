"""Config flow for OWM Precipitation Forecast."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import (CONF_API_KEY, CONF_LOCATION, CONF_SNOW_RATIO,
                    DEFAULT_SNOW_RATIO, DOMAIN)


class OWMPrecipitationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for OWM Precipitation Forecast."""

    @config_entries.HOMEASSISTANT_RESTART_REQUIRED
    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="OWM Precipitation", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_LOCATION): str,
                    vol.Optional(CONF_SNOW_RATIO, default=DEFAULT_SNOW_RATIO): vol.Coerce(float),
                }
            ),
        )

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SNOW_RATIO,
                        default=self.config_entry.options.get(CONF_SNOW_RATIO, DEFAULT_SNOW_RATIO),
                    ): vol.Coerce(float),
                }
            ),
        )
