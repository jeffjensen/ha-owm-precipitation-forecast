from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import NAME_PREFIX, UNIT_INCHES

class OWMHourlyRainSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement = UNIT_INCHES

    def __init__(self, coordinator, location):
        super().__init__(coordinator)
        self._attr_name = f"{NAME_PREFIX}{location}_hourly_rain"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.hourly[0].rain_in

class OWMDailySnowSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement = UNIT_INCHES

    def __init__(self, coordinator, location):
        super().__init__(coordinator)
        self._attr_name = f"{NAME_PREFIX}{location}_daily_snow"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.daily[0].snow_in
