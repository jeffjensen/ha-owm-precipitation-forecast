from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_get_current_platform
from homeassistant.util import dt as dt_util

from .const import DOMAIN, ENTITY_PREFIX, UNIT_INCHES, CONF_LOCATION_NAME, CONF_ENABLE_RAIN, CONF_ENABLE_SNOW
from .coordinator import OWMPrecipForecastCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = {
    "rain_hourly": SensorEntityDescription(
        key="rain_hourly",
        name="Rain Hourly",
        state_class=None,
    ),
    "rain_daily": SensorEntityDescription(
        key="rain_daily",
        name="Rain Daily",
        state_class=None,
    ),
    "rain_next24h": SensorEntityDescription(
        key="rain_next24h",
        name="Rain Next24h",
        unit_of_measurement=UNIT_INCHES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "snow_hourly": SensorEntityDescription(
        key="snow_hourly",
        name="Snow Hourly",
        state_class=None,
    ),
    "snow_daily": SensorEntityDescription(
        key="snow_daily",
        name="Snow Daily",
        state_class=None,
    ),
    "snow_next24h": SensorEntityDescription(
        key="snow_next24h",
        name="Snow Next24h",
        unit_of_measurement=UNIT_INCHES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "health": SensorEntityDescription(
        key="health",
        name="Health",
        state_class=None,
    ),
}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: OWMPrecipForecastCoordinator = hass.data[DOMAIN][entry.entry_id]
    location = entry.data[CONF_LOCATION_NAME].lower().replace(" ", "_")
    enable_rain = entry.options.get(CONF_ENABLE_RAIN, True)
    enable_snow = entry.options.get(CONF_ENABLE_SNOW, True)

    entities = []
    if enable_rain:
        entities.extend([
            OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["rain_hourly"]),
            OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["rain_daily"]),
            OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["rain_next24h"]),
        ])
    if enable_snow:
        entities.extend([
            OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["snow_hourly"]),
            OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["snow_daily"]),
            OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["snow_next24h"]),
        ])
    entities.append(OWMPrecipSensor(coordinator, entry, location, SENSOR_DESCRIPTIONS["health"]))

    async_add_entities(entities)

class OWMPrecipSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: OWMPrecipForecastCoordinator, entry: ConfigEntry, location: str, description: SensorEntityDescription) -> None:
        self.coordinator = coordinator
        self.entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = f"OWM Precipitation Forecast {description.name}"
        self._attr_entity_id = f"sensor.{ENTITY_PREFIX}{location}_{description.key}"

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data
        if self.entity_description.key.endswith("next24h"):
            return data.get(self.entity_description.key)
        elif self.entity_description.key == "health":
            return data.get("health")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        if "hourly" in self.entity_description.key:
            forecast = [{"datetime": dt_util.utc_from_timestamp(h["dt"]).isoformat(), "precipitation": h["rain" if "rain" in self.entity_description.key else "snow"]} for h in data["hourly"]]
        elif "daily" in self.entity_description.key:
            forecast = [{"datetime": dt_util.utc_from_timestamp(d["dt"]).isoformat(), "precipitation": d["rain" if "rain" in self.entity_description.key else "snow"]} for d in data["daily"]]
        else:
            return None
        return {"forecast": forecast}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
