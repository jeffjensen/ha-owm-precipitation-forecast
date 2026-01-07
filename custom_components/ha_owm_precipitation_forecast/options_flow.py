from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from .const import CONF_SCAN_INTERVAL, CONF_SNOW_RATIOS, DEFAULT_SCAN_INTERVAL, DEFAULT_SNOW_RATIOS

class OWMPrecipitationOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self._entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.In([900, 1800, 3600, 14400, 28800, 43200, 86400]),
                vol.Optional(
                    CONF_SNOW_RATIOS,
                    default=self._entry.options.get(
                        CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS
                    ),
                ): dict,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
