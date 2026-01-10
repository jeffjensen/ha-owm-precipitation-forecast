"""Sensor platform for OWM Precipitation Forecast."""

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_API_CALLS_REMAINING,
    ATTR_API_CALLS_TODAY,
    ATTR_COORDINATES,
    ATTR_ERROR_COUNT,
    ATTR_FORECAST_TIME,
    ATTR_HOURLY_BREAKDOWN,
    ATTR_LAST_ERROR,
    ATTR_LAST_UPDATE,
    ATTR_LOCATION,
    ATTR_NEXT_UPDATE,
    ATTR_STATUS,
    ATTR_TEMPERATURE,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DOMAIN,
    ENTITY_CATEGORY_DIAGNOSTIC,
    ENTITY_NAME_PREFIX,
    HEALTH_STATUS_OK,
    SENSOR_TYPE_DAILY_RAIN,
    SENSOR_TYPE_DAILY_SNOW,
    SENSOR_TYPE_HEALTH,
    SENSOR_TYPE_HOURLY_RAIN,
    SENSOR_TYPE_HOURLY_SNOW,
    SENSOR_TYPE_NEXT_24H_RAIN,
    SENSOR_TYPE_NEXT_24H_SNOW,
)
from .coordinator import OWMPrecipitationCoordinator
from .data_processor import PrecipitationCalculator
from .entity_types import SENSOR_TYPES, get_sensor_type
from .helpers import format_entity_name, get_precipitation_description

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OWM Precipitation sensors based on a config entry."""
    coordinator: OWMPrecipitationCoordinator = entry.runtime_data

    location_name = entry.data[CONF_LOCATION_NAME]
    enable_rain = entry.options.get(CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN)
    enable_snow = entry.options.get(CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW)

    entities: list[SensorEntity] = []

    # Add rain sensors if enabled
    if enable_rain:
        entities.extend([
            OWMPrecipitationSensor(
                coordinator, entry, location_name, SENSOR_TYPE_HOURLY_RAIN
            ),
            OWMPrecipitationSensor(
                coordinator, entry, location_name, SENSOR_TYPE_DAILY_RAIN
            ),
            OWMPrecipitationSensor(
                coordinator, entry, location_name, SENSOR_TYPE_NEXT_24H_RAIN
            ),
        ])

    # Add snow sensors if enabled
    if enable_snow:
        entities.extend([
            OWMPrecipitationSensor(
                coordinator, entry, location_name, SENSOR_TYPE_HOURLY_SNOW
            ),
            OWMPrecipitationSensor(
                coordinator, entry, location_name, SENSOR_TYPE_DAILY_SNOW
            ),
            OWMPrecipitationSensor(
                coordinator, entry, location_name, SENSOR_TYPE_NEXT_24H_SNOW
            ),
        ])

    # Always add health sensor
    entities.append(
        OWMHealthSensor(coordinator, entry, location_name)
    )

    async_add_entities(entities)
    _LOGGER.info(
        "Added %d sensors for %s (rain: %s, snow: %s)",
        len(entities),
        location_name,
        enable_rain,
        enable_snow,
    )


class OWMPrecipitationSensor(CoordinatorEntity[OWMPrecipitationCoordinator], SensorEntity):
    """Representation of an OWM Precipitation sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        entry: ConfigEntry,
        location_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.sensor_type = sensor_type
        self.location_name = location_name
        self._entry = entry

        # Get sensor description
        description = get_sensor_type(sensor_type)
        if description:
            self.entity_description = description

        # Set unique ID
        self._attr_unique_id = format_entity_name(
            ENTITY_NAME_PREFIX, location_name, sensor_type
        )

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"OWM Precipitation {location_name}",
            "manufacturer": "OpenWeatherMap",
            "model": "One Call API 3.0",
            "entry_type": "service",
        }

        _LOGGER.debug(
            "Initialized %s sensor for %s", sensor_type, location_name
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        calculator = PrecipitationCalculator(self.coordinator.data)

        try:
            if self.sensor_type == SENSOR_TYPE_HOURLY_RAIN:
                return calculator.get_hourly_rain(0)
            elif self.sensor_type == SENSOR_TYPE_HOURLY_SNOW:
                return calculator.get_hourly_snow(0)
            elif self.sensor_type == SENSOR_TYPE_DAILY_RAIN:
                return calculator.get_daily_rain(0)
            elif self.sensor_type == SENSOR_TYPE_DAILY_SNOW:
                return calculator.get_daily_snow(0)
            elif self.sensor_type == SENSOR_TYPE_NEXT_24H_RAIN:
                return calculator.get_next_24h_rain()
            elif self.sensor_type == SENSOR_TYPE_NEXT_24H_SNOW:
                return calculator.get_next_24h_snow()
        except Exception as err:
            _LOGGER.error(
                "Error calculating %s value: %s", self.sensor_type, err
            )
            return None

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        calculator = PrecipitationCalculator(self.coordinator.data)
        attributes: dict[str, Any] = {}

        try:
            # Common attributes
            attributes[ATTR_LOCATION] = self.location_name
            attributes[ATTR_COORDINATES] = {
                "latitude": self.coordinator.data.latitude,
                "longitude": self.coordinator.data.longitude,
            }
            attributes[ATTR_LAST_UPDATE] = self.coordinator.data.last_update.isoformat()

            # Add forecast time for hourly sensors
            if "hourly" in self.sensor_type:
                if self.coordinator.data.hourly_forecasts:
                    next_hour = self.coordinator.data.hourly_forecasts[0]
                    attributes[ATTR_FORECAST_TIME] = next_hour.timestamp.isoformat()
                    attributes[ATTR_TEMPERATURE] = next_hour.temperature_f

            # Add forecast time for daily sensors
            elif "daily" in self.sensor_type:
                if self.coordinator.data.daily_forecasts:
                    today = self.coordinator.data.daily_forecasts[0]
                    attributes[ATTR_FORECAST_TIME] = today.date.date().isoformat()
                    attributes[ATTR_TEMPERATURE] = {
                        "high": today.temperature_high_f,
                        "low": today.temperature_low_f,
                    }

            # Add hourly breakdown for charts
            if self.sensor_type == SENSOR_TYPE_HOURLY_RAIN:
                attributes[ATTR_HOURLY_BREAKDOWN] = calculator.get_hourly_breakdown_rain(24)
            elif self.sensor_type == SENSOR_TYPE_HOURLY_SNOW:
                attributes[ATTR_HOURLY_BREAKDOWN] = calculator.get_hourly_breakdown_snow(24)
            elif self.sensor_type == SENSOR_TYPE_NEXT_24H_RAIN:
                attributes[ATTR_HOURLY_BREAKDOWN] = calculator.get_hourly_breakdown_rain(24)
            elif self.sensor_type == SENSOR_TYPE_NEXT_24H_SNOW:
                attributes[ATTR_HOURLY_BREAKDOWN] = calculator.get_hourly_breakdown_snow(24)
            elif self.sensor_type == SENSOR_TYPE_DAILY_RAIN:
                attributes["daily_breakdown"] = calculator.get_daily_breakdown_rain(7)
            elif self.sensor_type == SENSOR_TYPE_DAILY_SNOW:
                attributes["daily_breakdown"] = calculator.get_daily_breakdown_snow(7)

            # Add precipitation description
            if self.native_value is not None:
                attributes["description"] = get_precipitation_description(
                    self.native_value
                )

        except Exception as err:
            _LOGGER.error(
                "Error building attributes for %s: %s", self.sensor_type, err
            )

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
        )


class OWMHealthSensor(CoordinatorEntity[OWMPrecipitationCoordinator], SensorEntity):
    """Representation of OWM integration health sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = ENTITY_CATEGORY_DIAGNOSTIC

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        entry: ConfigEntry,
        location_name: str,
    ) -> None:
        """Initialize the health sensor."""
        super().__init__(coordinator)

        self.location_name = location_name
        self._entry = entry

        # Get sensor description
        description = get_sensor_type(SENSOR_TYPE_HEALTH)
        if description:
            self.entity_description = description

        # Set unique ID
        self._attr_unique_id = format_entity_name(
            ENTITY_NAME_PREFIX, location_name, SENSOR_TYPE_HEALTH
        )

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"OWM Precipitation {location_name}",
            "manufacturer": "OpenWeatherMap",
            "model": "One Call API 3.0",
            "entry_type": "service",
        }

        _LOGGER.debug("Initialized health sensor for %s", location_name)

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.coordinator.health_status.status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        health = self.coordinator.health_status

        attributes = {
            ATTR_STATUS: health.status,
            ATTR_API_CALLS_TODAY: health.api_calls_today,
            ATTR_API_CALLS_REMAINING: health.api_calls_remaining,
            ATTR_ERROR_COUNT: health.error_count,
        }

        # Add last error if present
        if health.last_error:
            attributes[ATTR_LAST_ERROR] = health.last_error

        # Add update times if available
        if health.last_update:
            attributes[ATTR_LAST_UPDATE] = health.last_update.isoformat()

        if health.next_update:
            attributes[ATTR_NEXT_UPDATE] = health.next_update.isoformat()

        # Add location info
        attributes[ATTR_LOCATION] = self.location_name
        attributes[ATTR_COORDINATES] = {
            "latitude": self.coordinator.latitude,
            "longitude": self.coordinator.longitude,
        }

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Health sensor is always available to report status
        return True

    @property
    def icon(self) -> str:
        """Return the icon based on health status."""
        status = self.coordinator.health_status.status
        if status == HEALTH_STATUS_OK:
            return "mdi:heart-pulse"
        elif status == "warning":
            return "mdi:alert"
        elif status == "error":
            return "mdi:alert-circle"
        else:  # unavailable
            return "mdi:help-circle"
