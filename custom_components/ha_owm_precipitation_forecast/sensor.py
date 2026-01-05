"""Sensor platform for OWM Precipitation Forecast."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import StateType

from .const import (
    CONF_LOCATION_NAME,
    DOMAIN,
    ENTITY_PREFIX,
    LOGGER,
    SENSOR_DAILY_RAIN,
    SENSOR_DAILY_SNOW,
    SENSOR_HEALTH,
    SENSOR_HOURLY_RAIN,
    SENSOR_HOURLY_SNOW,
    SENSOR_NEXT24H_RAIN,
    SENSOR_NEXT24H_SNOW,
    UOM_INCHES,
    HEALTH_STATUS_OK,
    HEALTH_STATUS_ERROR,
    HEALTH_STATUS_UNAVAILABLE,
)
from .coordinator import OWMPrecipitationCoordinator

_LOGGER: logging.Logger = LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: OWMPrecipitationCoordinator = hass.data[DOMAIN][entry.entry_id]
    location_name = entry.data[CONF_LOCATION_NAME]
    
    sensors = [
        OWMHourlyRainSensor(coordinator, location_name),
        OWMHourlySnowSensor(coordinator, location_name),
        OWMDailyRainSensor(coordinator, location_name),
        OWMDailySnowSensor(coordinator, location_name),
        OWMNext24hRainSensor(coordinator, location_name),
        OWMNext24hSnowSensor(coordinator, location_name),
        OWMHealthSensor(coordinator, location_name),
    ]
    
    async_add_entities(sensors)


class OWMPrecipitationBaseSensor(SensorEntity):
    """Base class for OWM precipitation sensors."""

    _attr_has_entity_name = True
    _attr_attribution = "Data provided by OpenWeatherMap"

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.location_name = location_name
        self.sensor_type = sensor_type
        
        self._attr_unique_id = (
            f"{coordinator.latitude}_{coordinator.longitude}_{sensor_type}"
        )
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.latitude}_{coordinator.longitude}")},
            name=location_name,
            manufacturer="OpenWeatherMap",
            model="One Call API 3.0",
        )

    @property
    def available(self) -> bool:
        """Return availability."""
        return self.coordinator.last_error is None


class OWMHourlyRainSensor(OWMPrecipitationBaseSensor):
    """Hourly rain accumulation sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_HOURLY_RAIN)
        self._attr_name = "Hourly rain"
        self._attr_native_unit_of_measurement = UOM_INCHES
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        total = 0.0
        for hour in self.coordinator.data.get("hourly", []):
            total += hour.get("rain", 0.0)
        return round(total, 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes with hourly breakdown."""
        attrs = {}
        for i, hour in enumerate(self.coordinator.data.get("hourly", [])[:24]):
            attrs[f"hour_{i}_rain"] = round(hour.get("rain", 0.0), 4)
            attrs[f"hour_{i}_timestamp"] = hour.get("timestamp")
        return attrs


class OWMHourlySnowSensor(OWMPrecipitationBaseSensor):
    """Hourly snow accumulation sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_HOURLY_SNOW)
        self._attr_name = "Hourly snow"
        self._attr_native_unit_of_measurement = UOM_INCHES
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        total = 0.0
        for hour in self.coordinator.data.get("hourly", []):
            total += hour.get("snow", 0.0)
        return round(total, 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes with hourly breakdown."""
        attrs = {}
        for i, hour in enumerate(self.coordinator.data.get("hourly", [])[:24]):
            attrs[f"hour_{i}_snow"] = round(hour.get("snow", 0.0), 4)
            attrs[f"hour_{i}_timestamp"] = hour.get("timestamp")
        return attrs


class OWMDailyRainSensor(OWMPrecipitationBaseSensor):
    """Daily rain sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_DAILY_RAIN)
        self._attr_name = "Daily rain"
        self._attr_native_unit_of_measurement = UOM_INCHES
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        total = 0.0
        for day in self.coordinator.data.get("daily", [])[:1]:
            total += day.get("rain", 0.0)
        return round(total, 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes with daily breakdown."""
        attrs = {}
        for i, day in enumerate(self.coordinator.data.get("daily", [])[:8]):
            attrs[f"day_{i}_rain"] = round(day.get("rain", 0.0), 4)
            attrs[f"day_{i}_timestamp"] = day.get("timestamp")
        return attrs


class OWMDailySnowSensor(OWMPrecipitationBaseSensor):
    """Daily snow sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_DAILY_SNOW)
        self._attr_name = "Daily snow"
        self._attr_native_unit_of_measurement = UOM_INCHES
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        total = 0.0
        for day in self.coordinator.data.get("daily", [])[:1]:
            total += day.get("snow", 0.0)
        return round(total, 4)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes with daily breakdown."""
        attrs = {}
        for i, day in enumerate(self.coordinator.data.get("daily", [])[:8]):
            attrs[f"day_{i}_snow"] = round(day.get("snow", 0.0), 4)
            attrs[f"day_{i}_timestamp"] = day.get("timestamp")
        return attrs


class OWMNext24hRainSensor(OWMPrecipitationBaseSensor):
    """Next 24 hour rain accumulation sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_NEXT24H_RAIN)
        self._attr_name = "Next 24h rain"
        self._attr_native_unit_of_measurement = UOM_INCHES
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        return round(self.coordinator.data.get("next24h", {}).get("rain", 0.0), 4)


class OWMNext24hSnowSensor(OWMPrecipitationBaseSensor):
    """Next 24 hour snow accumulation sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_NEXT24H_SNOW)
        self._attr_name = "Next 24h snow"
        self._attr_native_unit_of_measurement = UOM_INCHES
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        return round(self.coordinator.data.get("next24h", {}).get("snow", 0.0), 4)


class OWMHealthSensor(OWMPrecipitationBaseSensor):
    """Integration health status sensor."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        location_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, location_name, SENSOR_HEALTH)
        self._attr_name = "Health"
        self._attr_entity_category = "diagnostic"

    @property
    def native_value(self) -> StateType:
        """Return health status."""
        if self.coordinator.last_error:
            return HEALTH_STATUS_ERROR
        if not self.coordinator.data:
            return HEALTH_STATUS_UNAVAILABLE
        return HEALTH_STATUS_OK

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return health attributes."""
        attrs = {
            "last_error": self.coordinator.last_error,
            "last_update": self.coordinator.data.get("last_update") if self.coordinator.data else None,
        }
        return attrs
