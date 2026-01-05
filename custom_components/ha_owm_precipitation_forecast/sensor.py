"""Sensor platform for precipitation forecast."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PrecipitationForecastCoordinator
from .calculator import PrecipitationCalculator
from .const import (
    ATTR_ACCUMULATION,
    ATTR_FORECAST_DATA,
    ATTR_LOCATION,
    ATTR_TEMPERATURE,
    ATTR_TIMESTAMP,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_SNOW_RATIOS,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_SNOW_RATIOS,
    DOMAIN,
    ENTITY_PREFIX,
    ENTITY_RAIN_DAILY,
    ENTITY_RAIN_HOURLY,
    ENTITY_RAIN_NEXT24H,
    ENTITY_SNOW_DAILY,
    ENTITY_SNOW_HOURLY,
    ENTITY_SNOW_NEXT24H,
    LOGGER_NAME,
    UNIT_INCHES,
)

_LOGGER = logging.getLogger(LOGGER_NAME)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: PrecipitationForecastCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Get configuration
    enable_rain = config_entry.options.get(
        CONF_ENABLE_RAIN,
        config_entry.data.get(CONF_ENABLE_RAIN, DEFAULT_ENABLE_RAIN),
    )
    enable_snow = config_entry.options.get(
        CONF_ENABLE_SNOW,
        config_entry.data.get(CONF_ENABLE_SNOW, DEFAULT_ENABLE_SNOW),
    )
    snow_ratios = config_entry.options.get(
        CONF_SNOW_RATIOS,
        config_entry.data.get(CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS),
    )

    location_name = config_entry.data[CONF_LOCATION_NAME]

    entities: list[SensorEntity] = []

    # Rain sensors
    if enable_rain:
        entities.extend([
            PrecipitationSensor(
                coordinator, location_name, "rain", "hourly", ENTITY_RAIN_HOURLY
            ),
            PrecipitationSensor(
                coordinator, location_name, "rain", "daily", ENTITY_RAIN_DAILY
            ),
            PrecipitationSensor(
                coordinator, location_name, "rain", "next24h", ENTITY_RAIN_NEXT24H
            ),
        ])

    # Snow sensors
    if enable_snow:
        entities.extend([
            PrecipitationSensor(
                coordinator, location_name, "snow", "hourly", ENTITY_SNOW_HOURLY, snow_ratios
            ),
            PrecipitationSensor(
                coordinator, location_name, "snow", "daily", ENTITY_SNOW_DAILY, snow_ratios
            ),
            PrecipitationSensor(
                coordinator, location_name, "snow", "next24h", ENTITY_SNOW_NEXT24H, snow_ratios
            ),
        ])

    async_add_entities(entities)


class PrecipitationSensor(CoordinatorEntity, SensorEntity):
    """Precipitation forecast sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.PRECIPITATION
    _attr_native_unit_of_measurement = UNIT_INCHES

    def __init__(
        self,
        coordinator: PrecipitationForecastCoordinator,
        location_name: str,
        precip_type: str,
        period: str,
        entity_suffix: str,
        snow_ratios: dict[str, float] | None = None,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        
        self.location_name = location_name.lower().replace(" ", "_")
        self.precip_type = precip_type
        self.period = period
        self.snow_ratios = snow_ratios or DEFAULT_SNOW_RATIOS
        
        self._attr_name = f"OWM Precipitation Forecast {location_name} {precip_type.title()} {period.replace('next', 'Next ')}"
        self._attr_unique_id = f"{ENTITY_PREFIX}_{self.location_name}_{entity_suffix}"
        
        self.calculator = PrecipitationCalculator(self.snow_ratios)

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        if self.period == "next24h":
            return self._calculate_next_24h()
        elif self.period == "hourly":
            forecast = self._get_hourly_forecast()
            return forecast[-1][ATTR_ACCUMULATION] if forecast else None
        else:  # daily
            forecast = self._get_daily_forecast()
            return forecast[-1][ATTR_ACCUMULATION] if forecast else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        attrs = {
            ATTR_LOCATION: {
                "name": self.location_name,
                "latitude": self.coordinator.client.latitude,
                "longitude": self.coordinator.client.longitude,
            }
        }

        if self.period == "hourly":
            attrs[ATTR_FORECAST_DATA] = self._get_hourly_forecast()
        elif self.period == "daily":
            attrs[ATTR_FORECAST_DATA] = self._get_daily_forecast()
        else:  # next24h
            attrs[ATTR_FORECAST_DATA] = self._get_next_24h_breakdown()

        return attrs

    def _calculate_next_24h(self) -> float:
        """Calculate total precipitation for next 24 hours."""
        hourly_data = self.coordinator.data.get("hourly", [])[:24]
        total = 0.0

        for hour in hourly_data:
            mm_value = hour.get(self.precip_type, 0.0)
            temp_f = hour.get("temperature", 32.0)

            if self.precip_type == "snow":
                total += self.calculator.mm_to_snow_inches(mm_value, temp_f)
            else:
                total += self.calculator.mm_to_inches(mm_value)

        return round(total, 2)

    def _get_hourly_forecast(self) -> list[dict[str, Any]]:
        """Get hourly forecast data."""
        hourly_data = self.coordinator.data.get("hourly", [])
        forecast = []

        for hour in hourly_data:
            mm_value = hour.get(self.precip_type, 0.0)
            temp_f = hour.get("temperature", 32.0)

            if self.precip_type == "snow":
                inches = self.calculator.mm_to_snow_inches(mm_value, temp_f)
            else:
                inches = self.calculator.mm_to_inches(mm_value)

            forecast.append({
                ATTR_TIMESTAMP: hour["timestamp"],
                ATTR_ACCUMULATION: round(inches, 2),
                ATTR_TEMPERATURE: temp_f,
            })

        return forecast

    def _get_daily_forecast(self) -> list[dict[str, Any]]:
        """Get daily forecast data."""
        daily_data = self.coordinator.data.get("daily", [])
        forecast = []

        for day in daily_data:
            mm_value = day.get(self.precip_type, 0.0)
            temp_f = day.get("temperature", 32.0)

            if self.precip_type == "snow":
                inches = self.calculator.mm_to_snow_inches(mm_value, temp_f)
            else:
                inches = self.calculator.mm_to_inches(mm_value)

            forecast.append({
                ATTR_TIMESTAMP: day["timestamp"],
                ATTR_ACCUMULATION: round(inches, 2),
                ATTR_TEMPERATURE: temp_f,
            })

        return forecast

    def _get_next_24h_breakdown(self) -> list[dict[str, Any]]:
        """Get hourly breakdown for next 24 hours."""
        return self._get_hourly_forecast()[:24]
