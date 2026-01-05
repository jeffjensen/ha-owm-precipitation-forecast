"""Config flow for OWM Precipitation Forecast."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN, CONF_API_KEY, CONF_LOCATION_NAME, CONF_LATITUDE, CONF_LONGITUDE,
    CONF_POLLING_INTERVAL, POLLING_OPTIONS,
    CONF_ENABLE_SNOW, CONF_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW, DEFAULT_ENABLE_RAIN, DEFAULT_POLLING_INTERVAL,
    CONF_RATIO_34_PLUS, CONF_RATIO_28_34, CONF_RATIO_20_28,
    CONF_RATIO_10_20, CONF_RATIO_0_10, CONF_RATIO_NEG,
    DEFAULT_RATIO_34_PLUS, DEFAULT_RATIO_28_34, DEFAULT_RATIO_20_28,
    DEFAULT_RATIO_10_20, DEFAULT_RATIO_0_10, DEFAULT_RATIO_NEG
)

class OWMPrecipitationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate? We could test the API key here.
            # For now, just create entry.
            return self.async_create_entry(
                title=user_input[CONF_LOCATION_NAME],
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_LOCATION_NAME, default=self.hass.config.location_name): str,
            vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): float,
            vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): float,
            vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.In(POLLING_OPTIONS),
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OWMPrecipitationOptionsFlow(config_entry)

class OWMPrecipitationOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values or defaults
        options = self.config_entry.options

        interval = options.get(CONF_POLLING_INTERVAL, self.config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))

        schema = vol.Schema({
            vol.Required(CONF_POLLING_INTERVAL, default=interval): vol.In(POLLING_OPTIONS),
            vol.Required(CONF_ENABLE_RAIN, default=options.get(CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN)): bool,
            vol.Required(CONF_ENABLE_SNOW, default=options.get(CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW)): bool,

            vol.Required(CONF_RATIO_34_PLUS, default=options.get(CONF_RATIO_34_PLUS, DEFAULT_RATIO_34_PLUS)): float,
            vol.Required(CONF_RATIO_28_34, default=options.get(CONF_RATIO_28_34, DEFAULT_RATIO_28_34)): float,
            vol.Required(CONF_RATIO_20_28, default=options.get(CONF_RATIO_20_28, DEFAULT_RATIO_20_28)): float,
            vol.Required(CONF_RATIO_10_20, default=options.get(CONF_RATIO_10_20, DEFAULT_RATIO_10_20)): float,
            vol.Required(CONF_RATIO_0_10, default=options.get(CONF_RATIO_0_10, DEFAULT_RATIO_0_10)): float,
            vol.Required(CONF_RATIO_NEG, default=options.get(CONF_RATIO_NEG, DEFAULT_RATIO_NEG)): float,
        })

        return self.async_show_form(step_id="init", data_schema=schema)