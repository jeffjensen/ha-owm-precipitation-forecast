from __future__ import annotations

from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import OWMPrecipitationCoordinator
from .sensor import OWMPrecipitationSensor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OWMPrecipitationCoordinator = hass.data[entry.domain][entry.entry_id]

    async_add_entities(
        [
            OWMPrecipitationSensor(coordinator, "rain"),
            OWMPrecipitationSensor(coordinator, "snow"),
        ]
    )
