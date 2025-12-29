from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .api import OWMPrecipitationTransformer
from .const import (
    ATTR_FORECAST_DATE,
    ATTR_FORECAST_HOURS,
    ATTR_FORECAST_TIMESTAMP,
    ATTR_LOCATION_NAME,
    ATTR_RAIN_IN,
    ATTR_SNOW_IN,
    ATTR_SNOW_RATIO_PROFILE,
    ATTR_SNOW_RATIO_USED,
    ATTR_TEMP_F,
    ATTR_TEMP_RANGE_F,
    CONF_LOCATION_NAME,
    CONF_LOCATION_SLUG,
    DOMAIN,
)
from .coordinator import OWMPrecipitationCoordinator
from .snow_ratio import SnowRatioCalculator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up precipitation forecast sensors for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: OWMPrecipitationCoordinator = data["coordinator"]
    snow_ratio: SnowRatioCalculator = data["snow_ratio"]

    transformer = OWMPrecipitationTransformer(snow_ratio)

    location_slug: str = entry.data[CONF_LOCATION_SLUG]
    location_name: str = entry.data[CONF_LOCATION_NAME]

    entities: list[SensorEntity] = []

    # Combined hourly
    entities.append(
        HourlyCombinedPrecipitationSensor(
            coordinator,
            transformer,
            location_slug,
            location_name,
            entry.entry_id,
        )
    )
    # Combined daily
    entities.append(
        DailyCombinedPrecipitationSensor(
            coordinator,
            transformer,
            location_slug,
            location_name,
            entry.entry_id,
        )
    )
    # Combined next24h
    entities.append(
        Next24hCombinedPrecipitationSensor(
            coordinator,
            transformer,
            location_slug,
            location_name,
            entry.entry_id,
        )
    )

    # You would also add rain/snow‑only sensors here:
    # - HourlyRainPrecipitationSensor
    # - HourlySnowPrecipitationSensor
    # - DailyRainPrecipitationSensor
    # - DailySnowPrecipitationSensor
    # - Next24hRainPrecipitationSensor
    # - Next24hSnowPrecipitationSensor

    async_add_entities(entities)


class BaseOWMPrecipitationSensor(SensorEntity):
    """Base precipitation sensor with shared behavior."""

    _attr_device_class = SensorDeviceClass.PRECIPITATION
    _attr_native_unit_of_measurement = "in"

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        transformer: OWMPrecipitationTransformer,
        location_slug: str,
        location_name: str,
        entry_id: str,
        metric_suffix: str,
        friendly_suffix: str,
    ) -> None:
        self._coordinator = coordinator
        self._transformer = transformer
        self._location_slug = location_slug
        self._location_name = location_name
        self._entry_id = entry_id
        # Entity ID is driven by unique_id; HA will prepend "sensor."
        self._attr_unique_id = (
            f"owm_precipitation_forecast_{location_slug}_{metric_suffix}"
        )
        self._attr_name = (
            f"OWM Precipitation Forecast {location_name} {friendly_suffix}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=f"OWM Precipitation Forecast {self._location_name}",
            manufacturer="OpenWeatherMap",
            model="OWM One Call 3.0",
        )

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    async def async_update(self) -> None:
        await self._coordinator.async_request_refresh()

    @property
    def _raw_hourly(self) -> list[dict[str, Any]]:
        return self._coordinator.data.get("hourly", [])

    @property
    def _raw_daily(self) -> list[dict[str, Any]]:
        return self._coordinator.data.get("daily", [])


class HourlyCombinedPrecipitationSensor(BaseOWMPrecipitationSensor):
    """Combined hourly precipitation for current/next hour."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        transformer: OWMPrecipitationTransformer,
        location_slug: str,
        location_name: str,
        entry_id: str,
    ) -> None:
        super().__init__(
            coordinator,
            transformer,
            location_slug,
            location_name,
            entry_id,
            metric_suffix="precipitation_hourly",
            friendly_suffix="Precipitation Hourly",
        )

    @property
    def native_value(self) -> float:
        hourly_points = self._transformer.build_hourly_points(self._raw_hourly)
        if not hourly_points:
            return 0.0
        p = hourly_points[0]
        return p.rain_inches + p.snow_inches

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        hourly_points = self._transformer.build_hourly_points(self._raw_hourly)
        if not hourly_points:
            return {}
        p = hourly_points[0]
        return {
            ATTR_RAIN_IN: p.rain_inches,
            ATTR_SNOW_IN: p.snow_inches,
            ATTR_TEMP_F: p.temperature_f,
            ATTR_SNOW_RATIO_USED: p.snow_ratio_used,
            ATTR_FORECAST_TIMESTAMP: p.timestamp.isoformat(),
            ATTR_LOCATION_NAME: self._location_name,
        }


class DailyCombinedPrecipitationSensor(BaseOWMPrecipitationSensor):
    """Combined daily precipitation for today / next day."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        transformer: OWMPrecipitationTransformer,
        location_slug: str,
        location_name: str,
        entry_id: str,
    ) -> None:
        super().__init__(
            coordinator,
            transformer,
            location_slug,
            location_name,
            entry_id,
            metric_suffix="precipitation_daily",
            friendly_suffix="Precipitation Daily",
        )

    @property
    def native_value(self) -> float:
        daily_point = self._transformer.summarize_daily(self._raw_daily)
        return daily_point.rain_inches + daily_point.snow_inches

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        daily_point = self._transformer.summarize_daily(self._raw_daily)
        temp_min_f, temp_max_f = daily_point.temperature_range_f
        return {
            ATTR_RAIN_IN: daily_point.rain_inches,
            ATTR_SNOW_IN: daily_point.snow_inches,
            ATTR_TEMP_RANGE_F: (temp_min_f, temp_max_f),
            ATTR_SNOW_RATIO_PROFILE: daily_point.snow_ratio_profile,
            ATTR_FORECAST_DATE: daily_point.date.date().isoformat(),
            ATTR_LOCATION_NAME: self._location_name,
        }


class Next24hCombinedPrecipitationSensor(BaseOWMPrecipitationSensor):
    """Combined precipitation for the next 24 hours."""

    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        transformer: OWMPrecipitationTransformer,
        location_slug: str,
        location_name: str,
        entry_id: str,
    ) -> None:
        super().__init__(
            coordinator,
            transformer,
            location_slug,
            location_name,
            entry_id,
            metric_suffix="precipitation_next24h",
            friendly_suffix="Precipitation Next 24h",
        )

    @property
    def native_value(self) -> float:
        hourly_points = self._transformer.build_hourly_points(self._raw_hourly)
        summary = self._transformer.summarize_next24h(hourly_points)
        return summary[ATTR_RAIN_IN] + summary[ATTR_SNOW_IN]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        hourly_points = self._transformer.build_hourly_points(self._raw_hourly)
        summary = self._transformer.summarize_next24h(hourly_points)
        temp_min_f, temp_max_f = summary[ATTR_TEMP_RANGE_F]
        return {
            ATTR_RAIN_IN: summary[ATTR_RAIN_IN],
            ATTR_SNOW_IN: summary[ATTR_SNOW_IN],
            ATTR_TEMP_RANGE_F: (temp_min_f, temp_max_f),
            ATTR_SNOW_RATIO_PROFILE: summary[ATTR_SNOW_RATIO_PROFILE],
            ATTR_FORECAST_HOURS: 24,
            ATTR_LOCATION_NAME: self._location_name,
        }
