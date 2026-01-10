"""Entity type definitions for OWM Precipitation Forecast."""

from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import SensorEntityDescription

from .const import (
    ICON_HEALTH,
    ICON_RAIN,
    ICON_SNOW,
    SENSOR_TYPE_DAILY_RAIN,
    SENSOR_TYPE_DAILY_SNOW,
    SENSOR_TYPE_HEALTH,
    SENSOR_TYPE_HOURLY_RAIN,
    SENSOR_TYPE_HOURLY_SNOW,
    SENSOR_TYPE_NEXT_24H_RAIN,
    SENSOR_TYPE_NEXT_24H_SNOW,
    STATE_CLASS_MEASUREMENT,
    UNIT_INCHES,
)


@dataclass(frozen=True)
class OWMPrecipitationSensorEntityDescription(SensorEntityDescription):
    """Describes OWM Precipitation sensor entity."""

    value_fn: Callable[[Any], float | str | None] | None = None
    attributes_fn: Callable[[Any], dict[str, Any]] | None = None


SENSOR_TYPES: tuple[OWMPrecipitationSensorEntityDescription, ...] = (
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_HOURLY_RAIN,
        translation_key="hourly_rain",
        icon=ICON_RAIN,
        native_unit_of_measurement=UNIT_INCHES,
        state_class=STATE_CLASS_MEASUREMENT,
        suggested_display_precision=2,
    ),
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_HOURLY_SNOW,
        translation_key="hourly_snow",
        icon=ICON_SNOW,
        native_unit_of_measurement=UNIT_INCHES,
        state_class=STATE_CLASS_MEASUREMENT,
        suggested_display_precision=2,
    ),
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_DAILY_RAIN,
        translation_key="daily_rain",
        icon=ICON_RAIN,
        native_unit_of_measurement=UNIT_INCHES,
        state_class=STATE_CLASS_MEASUREMENT,
        suggested_display_precision=2,
    ),
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_DAILY_SNOW,
        translation_key="daily_snow",
        icon=ICON_SNOW,
        native_unit_of_measurement=UNIT_INCHES,
        state_class=STATE_CLASS_MEASUREMENT,
        suggested_display_precision=2,
    ),
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_NEXT_24H_RAIN,
        translation_key="next24h_rain",
        icon=ICON_RAIN,
        native_unit_of_measurement=UNIT_INCHES,
        state_class=STATE_CLASS_MEASUREMENT,
        suggested_display_precision=2,
    ),
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_NEXT_24H_SNOW,
        translation_key="next24h_snow",
        icon=ICON_SNOW,
        native_unit_of_measurement=UNIT_INCHES,
        state_class=STATE_CLASS_MEASUREMENT,
        suggested_display_precision=2,
    ),
    OWMPrecipitationSensorEntityDescription(
        key=SENSOR_TYPE_HEALTH,
        translation_key="health",
        icon=ICON_HEALTH,
        entity_registry_enabled_default=True,
    ),
)


def get_sensor_type(sensor_type: str) -> OWMPrecipitationSensorEntityDescription | None:
    """Get sensor type description by key."""
    for sensor in SENSOR_TYPES:
        if sensor.key == sensor_type:
            return sensor
    return None
