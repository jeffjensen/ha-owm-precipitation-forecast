"""Binary sensor platform for health monitoring."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PrecipitationForecastCoordinator
from .const import (
    CONF_LOCATION_NAME,
    DOMAIN,
    ENTITY_HEALTH,
    ENTITY_PREFIX,
    LOGGER_NAME,
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
)

_LOGGER = logging.getLogger(LOGGER_NAME)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator: PrecipitationForecastCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    location_name = config_entry.data[CONF_LOCATION_NAME]

    async_add_entities([IntegrationHealthSensor(coordinator, location_name)])


class IntegrationHealthSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for integration health."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: PrecipitationForecastCoordinator,
        location_name: str,
    ) -> None:
        """Initialize health sensor."""
        super().__init__(coordinator)
        
        self.location_name = location_name.lower().replace(" ", "_")
        
        self._attr_name = f"OWM Precipitation Forecast {location_name} Health"
        self._attr_unique_id = f"{ENTITY_PREFIX}_{self.location_name}_{ENTITY_HEALTH}"

    @property
    def is_on(self) -> bool:
        """Return True if there's a problem."""
        return self.coordinator.last_error is not None or self.coordinator.error_count > 3

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        status = STATUS_OK
        if self.coordinator.error_count > 3:
            status = STATUS_ERROR
        elif self.coordinator.error_count > 0:
            status = STATUS_WARNING

        return {
            "last_update": datetime.now().isoformat() if self.coordinator.data else None,
            "api_status": status,
            "error_count": self.coordinator.error_count,
            "last_error": self.coordinator.last_error,
        }
