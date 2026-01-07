from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import NAME_PREFIX, UNIT_INCHES

class _BasePrecipSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement = UNIT_INCHES

    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._attr_name = name

class HourlyRainSensor(_BasePrecipSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{NAME_PREFIX}{location}_hourly_rain")

    @property
    def native_value(self):
        return self.coordinator.data.hourly[0].rain_in if self.coordinator.data else None

class HourlySnowSensor(_BasePrecipSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{NAME_PREFIX}{location}_hourly_snow")

    @property
    def native_value(self):
        return self.coordinator.data.hourly[0].snow_in if self.coordinator.data else None

class DailyRainSensor(_BasePrecipSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{NAME_PREFIX}{location}_daily_rain")

    @property
    def native_value(self):
        return self.coordinator.data.daily[0].rain_in if self.coordinator.data else None

class DailySnowSensor(_BasePrecipSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{NAME_PREFIX}{location}_daily_snow")

    @property
    def native_value(self):
        return self.coordinator.data.daily[0].snow_in if self.coordinator.data else None

class Next24hRainSensor(_BasePrecipSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{NAME_PREFIX}{location}_next24h_rain")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return sum(h.rain_in for h in self.coordinator.data.hourly[:24])

class Next24hSnowSensor(_BasePrecipSensor):
    def __init__(self, coordinator, location):
        super().__init__(coordinator, f"{NAME_PREFIX}{location}_next24h_snow")

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return sum(h.snow_in for h in self.coordinator.data.hourly[:24])
