from __future__ import annotations

from typing import Any
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[misc]
    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="OWM Precipitation", data=user_input)

        return self.async_show_form(step_id="user", data_schema=None)
