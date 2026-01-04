# Sensor platform that creates all precipitation and health sensors.
# Creates all sensor entities
# Manages rain and snow sensors based on configuration
# Provides health monitoring sensor
# Rich attributes for automation and charting

"""Sensor platform for OpenWeatherMap Precipitation Forecast."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_LOCATION_NAME,
    DOMAIN,
    ENTITY_HEALTH,
    ENTITY_PREFIX,
    ENTITY_RAIN_DAILY,
    ENTITY_RAIN_HOURLY,
    ENTITY_RAIN_NEXT24H,
    ENTITY_SNOW_DAILY,
    ENTITY_SNOW_HOURLY,
    ENTITY_SNOW_NEXT24H,
    INCHES_TO_CM,
    UNIT_INCHES,
)
from .coordinator import OWMPrecipitationCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: OWMPrecipitationCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    location_name = config_entry.data.get(CONF_LOCATION_NAME, DEFAULT_LOCATION_NAME)
    enable_rain = config_entry.options.get(CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN)
    enable_snow = config_entry.options.get(CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW)

    entities: list[SensorEntity] = []

    # Add rain sensors
    if enable_rain:
        entities.extend([
            OWMPrecipitationSensor(
                coordinator,
                location_name,
                ENTITY_RAIN_HOURLY,
                "Rain Hourly",
                "hourly_rain"
            ),
            OWMPrecipitationSensor(
                coordinator,
                location_name,
                ENTITY_RAIN_DAILY,
                "Rain Daily",
                "daily_rain"
            ),
            OWMPrecipitationSensor(
                coordinator,
                location_name,
                ENTITY_RAIN_NEXT24H,
                "Rain Next 24h",
                "next24h_rain"
            ),
        ])
        _LOGGER.debug("Added rain sensors for %s", location_name)

    # Add snow sensors
    if enable_snow:
        entities.extend([
            OWMPrecipitationSensor(
                coordinator,
                location_name,
                ENTITY_SNOW_HOURLY,
                "Snow Hourly",
                "hourly_snow"
            ),
            OWMPrecipitationSensor(
                coordinator,
                location_name,
                ENTITY_SNOW_DAILY,
                "Snow Daily",
                "daily_snow"
            ),
            OWMPrecipitationSensor(
                coordinator,
                location_name,
                ENTITY_SNOW_NEXT24H,
                "Snow Next 24h",
                "next24h_snow"
            ),
        ])
        _LOGGER.debug("Added snow sensors for %s", location_name)

    # Always add health sensor
    entities.append(OWMHealthSensor(coordinator, location_name))
    _LOGGER.debug("Added health sensor for %s", location_name)

    async_add_entities(entities)
    _LOGGER.info("Setup complete: %d sensors added for %s", len(entities), location_name)


class OWMPrecipitationSensor(CoordinatorEntity, SensorEntity):
    """Representation of an OWM Precipitation Sensor."""

    _attr_device_class = SensorDeviceClass.PRECIPITATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UNIT_INCHES

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
        sensor_type: str,
        friendly_name: str,
        data_key: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data update coordinator
            location_name: Name of the location
            sensor_type: Type identifier for the sensor
            friendly_name: Human-readable sensor name
            data_key: Key to access data in coordinator
        """
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._location_name = location_name
        self._data_key = data_key
        self._friendly_name = friendly_name

        # Create entity ID with location name
        safe_location = location_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{ENTITY_PREFIX}_{safe_location}_{sensor_type}"
        self._attr_name = f"{ENTITY_PREFIX}_{safe_location}_{sensor_type}"
        self._attr_translation_key = sensor_type

        _LOGGER.debug("Initialized sensor: %s", self._attr_unique_id)

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor.

        Returns:
            Current precipitation value in inches, or None if unavailable
        """
        if not self.coordinator.data:
            return None

        data = self.coordinator.data.get(self._data_key)

        # For next24h sensors, data is a direct float value
        if self._data_key in ["next24h_rain", "next24h_snow"]:
            return data

        # For hourly/daily sensors, get the most recent forecast value
        if isinstance(data, list) and data:
            key = "rain_inches" if "rain" in self._data_key else "snow_inches"
            return data[0].get(key)

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of additional sensor attributes
        """
        if not self.coordinator.data:
            return {}

        data = self.coordinator.data.get(self._data_key)

        attrs = {
            "unit_of_measurement": UNIT_INCHES,
            "last_update": self.coordinator.data.get("last_update"),
            "location": self._location_name,
        }

        # For next24h sensors, include total and conversion to cm
        if self._data_key in ["next24h_rain", "next24h_snow"]:
            if data is not None:
                attrs["total_inches"] = round(data, 3)
                attrs["total_cm"] = round(data * INCHES_TO_CM, 2)

        # For hourly/daily sensors, include forecast array
        elif isinstance(data, list):
            # Include up to 10 forecast entries for charts/cards
            attrs["forecast"] = data[:10]
            attrs["forecast_count"] = len(data)

            # Calculate totals for convenience
            if data:
                key = "rain_inches" if "rain" in self._data_key else "snow_inches"
                total = sum(entry.get(key, 0) for entry in data[:24])  # Next 24 entries
                attrs["total_forecast_inches"] = round(total, 3)
                attrs["total_forecast_cm"] = round(total * INCHES_TO_CM, 2)

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if coordinator has data and no critical errors
        """
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
        )


class OWMHealthSensor(CoordinatorEntity, SensorEntity):
    """Health monitoring sensor for the integration."""

    _attr_device_class = None
    _attr_state_class = None

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the health sensor.

        Args:
            coordinator: Data update coordinator
            location_name: Name of the location
        """
        super().__init__(coordinator)
        self._location_name = location_name

        # Create entity ID
        safe_location = location_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{ENTITY_PREFIX}_{safe_location}_{ENTITY_HEALTH}"
        self._attr_name = f"{ENTITY_PREFIX}_{safe_location}_{ENTITY_HEALTH}"
        self._attr_translation_key = ENTITY_HEALTH

        _LOGGER.debug("Initialized health sensor: %s", self._attr_unique_id)

    @property
    def native_value(self) -> str:
        """Return the health status.

        Returns:
            Health status: ok, warning, or error
        """
        return self.coordinator.health_status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the health attributes.

        Returns:
            Dictionary of health-related attributes
        """
        attrs = {
            "message": self.coordinator.health_message,
            "location": self._location_name,
            "last_successful_update": self.coordinator.last_update_success_time,
        }

        if self.coordinator.data:
            attrs["last_data_update"] = self.coordinator.data.get("last_update")

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            Always True - health sensor should always be available
        """
        return True

    @property
    def icon(self) -> str:
        """Return the icon based on health status.

        Returns:
            MDI icon name
        """
        status = self.coordinator.health_status
        if status == "ok":
            return "mdi:check-circle"
        elif status == "warning":
            return "mdi:alert-circle"
        elif status == "error":
            return "mdi:alert-circle-outline"
        return "mdi:help-circle"
