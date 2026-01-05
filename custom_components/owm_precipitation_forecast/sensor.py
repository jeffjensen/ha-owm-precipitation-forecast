"""Sensor platform for OWM Precipitation."""
from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfLength

from .const import DOMAIN, CONF_LOCATION_NAME, CONF_ENABLE_SNOW, CONF_ENABLE_RAIN, DEFAULT_ENABLE_SNOW, DEFAULT_ENABLE_RAIN, ATTRIBUTION
from .coordinator import OWMPrecipitationCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Setup sensor platform."""
    coordinator: OWMPrecipitationCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    location_name = entry.data[CONF_LOCATION_NAME]

    # Check toggles
    enable_rain = entry.options.get(CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN)
    enable_snow = entry.options.get(CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW)

    # Health Sensor
    entities.append(OWMHealthSensor(coordinator, location_name))

    if enable_rain:
        entities.append(OWMPrecipitationSensor(coordinator, location_name, "rain", "next24h"))
        entities.append(OWMPrecipitationSensor(coordinator, location_name, "rain", "daily"))
        entities.append(OWMPrecipitationSensor(coordinator, location_name, "rain", "hourly"))

    if enable_snow:
        entities.append(OWMPrecipitationSensor(coordinator, location_name, "snow", "next24h"))
        entities.append(OWMPrecipitationSensor(coordinator, location_name, "snow", "daily"))
        entities.append(OWMPrecipitationSensor(coordinator, location_name, "snow", "hourly"))

    async_add_entities(entities)

class OWMHealthSensor(CoordinatorEntity, SensorEntity):
    """Representation of the integration health."""

    def __init__(self, coordinator, location_name):
        super().__init__(coordinator)
        self._location_name = location_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_health"
        self._attr_name = f"owm_precipitation_forecast_{location_name}_health"
        self._attr_icon = "mdi:check-network"

    @property
    def native_value(self):
        return "OK" if self.coordinator.last_update_success else "Error"

    @property
    def extra_state_attributes(self):
        return {
            "last_updated": self.coordinator.last_update_success_time,
            "api_timestamp": self.coordinator.data.get("api_timestamp") if self.coordinator.data else None
        }

class OWMPrecipitationSensor(CoordinatorEntity, SensorEntity):
    """Representation of a precipitation sensor."""

    _attr_has_entity_name = False # We construct full name manually as requested
    _attr_device_class = SensorDeviceClass.PRECIPITATION
    _attr_native_unit_of_measurement = UnitOfLength.INCHES
    _attr_state_class = SensorStateClass.TOTAL
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator, location_name, precip_type, forecast_type):
        super().__init__(coordinator)
        self._precip_type = precip_type # rain or snow
        self._forecast_type = forecast_type # next24h, daily, hourly
        self._location_name = location_name.lower().replace(" ", "_")

        # Naming requirement: owm_precipitation_forecast_[location]_[type]_[forecast]
        self._attr_name = f"owm_precipitation_forecast_{self._location_name}_{precip_type}_{forecast_type}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{precip_type}_{forecast_type}"

        if precip_type == "snow":
            self._attr_icon = "mdi:snowflake"
        else:
            self._attr_icon = "mdi:weather-rainy"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data[self._precip_type]

        if self._forecast_type == "next24h":
            return round(data["next24h"], 2)

        # For Hourly/Daily, the state is the immediate next value, attributes hold the array
        if self._forecast_type == "hourly":
            if data["hourly"]:
                return round(data["hourly"][0]["val"], 2)
            return 0.0

        if self._forecast_type == "daily":
             if data["daily"]:
                return round(data["daily"][0]["val"], 2)
             return 0.0

        return 0.0

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        data = self.coordinator.data[self._precip_type]

        if self._forecast_type == "hourly":
            return {"forecast": data["hourly"]}
        elif self._forecast_type == "daily":
            return {"forecast": data["daily"]}

        return {}