from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_API_STATUS,
    ATTR_CONSECUTIVE_FAILURES,
    ATTR_LAST_API_ERROR,
    ATTR_LAST_SUCCESSFUL_UPDATE,
    ATTR_POLLING_INTERVAL_MINUTES,
    ATTR_LOCATION_NAME,
    CONF_LOCATION_NAME,
    CONF_LOCATION_SLUG,
    DOMAIN,
)
from .coordinator import OWMPrecipitationCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: OWMPrecipitationCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    location_slug: str = entry.data[CONF_LOCATION_SLUG]
    location_name: str = entry.data[CONF_LOCATION_NAME]
    async_add_entities(
        [
            OWMPrecipitationHealthBinarySensor(
                coordinator, location_slug, location_name, entry.entry_id
            )
        ]
    )


class OWMPrecipitationHealthBinarySensor(BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_slug: str,
        location_name: str,
        entry_id: str,
    ) -> None:
        self._coordinator = coordinator
        self._location_slug = location_slug
        self._location_name = location_name
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{location_slug}_health"
        self._attr_name = f"OWM Precipitation Forecast {location_name} Health"

    @property
    def is_on(self) -> bool:
        # on = problem; invert coordinator health
        health = self._coordinator.health
        status = health[ATTR_API_STATUS]
        return status != "ok"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        health = self._coordinator.health
        return {
            ATTR_LAST_SUCCESSFUL_UPDATE: health[ATTR_LAST_SUCCESSFUL_UPDATE],
            ATTR_LAST_API_ERROR: health[ATTR_LAST_API_ERROR],
            ATTR_CONSECUTIVE_FAILURES: health[ATTR_CONSECUTIVE_FAILURES],
            ATTR_API_STATUS: health[ATTR_API_STATUS],
            ATTR_LOCATION_NAME: self._location_name,
        }
