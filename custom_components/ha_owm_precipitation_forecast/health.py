
from homeassistant.components.sensor import SensorEntity

class OWMPrecipitationHealthSensor(SensorEntity):
    _attr_name = "owm_precipitation_forecast_health"

    def __init__(self, coordinator):
        self._coordinator = coordinator

    @property
    def native_value(self):
        return "ok" if self._coordinator.last_update_success else "error"
