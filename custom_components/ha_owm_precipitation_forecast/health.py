from __future__ import annotations

from typing import Any
from homeassistant.core import HomeAssistant, callback


@callback
def async_register(hass: HomeAssistant) -> None:
    return None


def async_healthcheck(hass: HomeAssistant) -> float | None:
    return None
