from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import NAME_PREFIX

class OWMPrecipitationHealthSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:heart-pulse"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = f"{NAME_PREFIX}health"

    @property
    def native_value(self) -> float | None:
        if self.coordinator.last_update_success:
            return "ok"
        return "error"

    @property
    def extra_state_attributes(self):
        return {
            "last_error": self.coordinator.last_error,
            "last_update_success": self.coordinator.last_update_success,
        }
