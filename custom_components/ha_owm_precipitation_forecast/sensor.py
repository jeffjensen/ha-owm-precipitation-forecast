
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import NAME_PREFIX, UNIT_INCHES

class OWMBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement = UNIT_INCHES

    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = f"{NAME_PREFIX}{name}"

class OWMNext24hRainSensor(OWMBaseSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{location}_rain_next24h")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return round(sum(h.rain_in for h in self.coordinator.data.hourly[:24]), 2)

class OWMNext24hSnowSensor(OWMBaseSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{location}_snow_next24h")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return round(sum(h.snow_in for h in self.coordinator.data.hourly[:24]), 2)
