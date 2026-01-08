from __future__ import annotations

from typing import Any
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    @callback
    def async_create_entry(self, data: dict[str, Any]) -> config_entries.FlowResult:
        return self.async_create_entry(title="", data=data)
