from homeassistant.components.sensor import SensorEntity
from .const import NAME_PREFIX, UNIT_INCHES

class OWMPrecipSensor(SensorEntity):
    _attr_native_unit_of_measurement = UNIT_INCHES
    def __init__(self, name):
        self._attr_name = f"{NAME_PREFIX}{name}"
        self._attr_native_value = 0.0
